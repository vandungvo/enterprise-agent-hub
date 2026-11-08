"""Shared plumbing for the non-Anthropic backends (gemini.py, openai_compat.py)."""
from __future__ import annotations

import asyncio
import json
import logging

import httpx

log = logging.getLogger("agenthub.providers")

RETRY_STATUSES = {429, 500, 502, 503, 504}
MAX_RETRY_WAIT = 60.0  # seconds; free tiers (e.g. Groq tokens-per-minute) ask for waits of up to a minute


class ProviderError(Exception):
    """HTTP error from an LLM provider; reported to the user as "Lỗi gọi model (status): message"."""

    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(f"{status_code}: {message}")
        self.status_code = status_code
        self.message = message


class ProviderConnectionError(Exception):
    def __init__(self, provider: str, detail: str = "") -> None:
        super().__init__(f"{provider}: {detail}")
        self.provider = provider


def _retry_wait(resp: httpx.Response, attempt: int) -> float:
    raw = resp.headers.get("retry-after")
    try:
        wait = float(raw) if raw else 2.0 ** attempt
    except ValueError:
        wait = 2.0 ** attempt
    return min(max(wait, 0.5), MAX_RETRY_WAIT)


async def open_stream(http: httpx.AsyncClient, provider: str, url: str, headers: dict, body: dict,
                      max_retries: int) -> httpx.Response:
    """POSTs `body` and returns the open streaming response; retries 429/5xx and transport errors."""
    for attempt in range(max_retries + 1):
        try:
            resp = await http.send(http.build_request("POST", url, json=body, headers=headers), stream=True)
        except httpx.TransportError as exc:
            if attempt < max_retries:
                await asyncio.sleep(2.0 ** attempt)
                continue
            raise ProviderConnectionError(provider, str(exc)) from exc
        if resp.status_code < 400:
            return resp
        raw = await resp.aread()
        await resp.aclose()
        try:
            err = json.loads(raw)["error"]
            message = err["message"] if isinstance(err, dict) else str(err)
        except Exception:
            message = raw.decode("utf-8", "replace")[:500]
        if resp.status_code in RETRY_STATUSES and attempt < max_retries:
            wait = _retry_wait(resp, attempt)
            log.warning("%s HTTP %s, retrying in %.1fs: %.200s", provider, resp.status_code, wait, message)
            await asyncio.sleep(wait)
            continue
        raise ProviderError(resp.status_code, message)
    raise ProviderError(503, f"{provider} không phản hồi")  # unreachable
