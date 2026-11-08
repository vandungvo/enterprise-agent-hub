"""Google Gemini backend behind the subset of the AsyncAnthropic interface the runtime uses.

The runtime (orchestrator.py) and the persisted conversation history stay in Anthropic Messages
format; this module translates each call:

    client.beta.messages.stream(**params)  ──▶  POST models/{model}:streamGenerateContent?alt=sse
        async for event in stream          ◀──  {"type": "text", "text": ...} per text delta
        await stream.get_final_message()   ◀──  BetaMessage (text / tool_use blocks, stop_reason, usage)

Mapping:
    system blocks          → systemInstruction
    assistant / user       → model / user
    tool_use               → functionCall   (Gemini's thoughtSignature kept on the block as `thought_signature`)
    tool_result            → functionResponse (name resolved from the matching tool_use)
    tools[].input_schema   → functionDeclarations[].parametersJsonSchema
    tool_choice none|auto  → functionCallingConfig.mode NONE|AUTO
    finishReason           → stop_reason (tool_use, end_turn, max_tokens, refusal)

Anthropic-only params (cache_control, output_config/effort, betas, fallbacks) are ignored.
"""
from __future__ import annotations

import json
import logging
import uuid
from types import SimpleNamespace
from typing import Any

import httpx
from anthropic.types.beta import BetaMessage

from app.llm.base import ProviderError, open_stream

log = logging.getLogger("agenthub.gemini")

API_BASE = "https://generativelanguage.googleapis.com/v1beta"
MAX_OUTPUT_TOKENS = 65_536
REFUSAL_REASONS = {"SAFETY", "RECITATION", "BLOCKLIST", "PROHIBITED_CONTENT", "SPII", "IMAGE_SAFETY",
                   "LANGUAGE", "OTHER"}
# Gemini 3 rejects function calls in the current turn that lack a thought signature. History written
# by another model (e.g. Claude) has none; Google documents this placeholder for that case.
DUMMY_SIGNATURE = "skip_thought_signature_validator"


GeminiError = ProviderError


# ---------------------------------------------------------------------------- request conversion
def _tool_result_text(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return json.dumps(content, ensure_ascii=False, default=str)


def to_contents(messages: list[dict]) -> list[dict]:
    names: dict[str, str] = {}
    contents = []
    for m in messages:
        role = "model" if m["role"] == "assistant" else "user"
        content = m["content"]
        parts: list[dict] = []
        if isinstance(content, str):
            if content:
                parts.append({"text": content})
        else:
            for b in content:
                kind = b.get("type")
                if kind == "text" and b.get("text"):
                    part = {"text": b["text"]}
                    if b.get("thought_signature"):
                        part["thoughtSignature"] = b["thought_signature"]
                    parts.append(part)
                elif kind == "tool_use":
                    names[b["id"]] = b["name"]
                    parts.append({"functionCall": {"name": b["name"], "args": b.get("input") or {}},
                                  "thoughtSignature": b.get("thought_signature") or DUMMY_SIGNATURE})
                elif kind == "tool_result":
                    key = "error" if b.get("is_error") else "result"
                    parts.append({"functionResponse": {"name": names.get(b["tool_use_id"], "tool"),
                                                       "response": {key: _tool_result_text(b.get("content"))}}})
                # thinking / server-tool blocks from other providers carry nothing Gemini can use
        if parts:
            contents.append({"role": role, "parts": parts})
    return contents


def to_request(params: dict) -> dict:
    body: dict[str, Any] = {"contents": to_contents(params["messages"])}
    system = params.get("system")
    if system:
        blocks = [system] if isinstance(system, str) else [b["text"] for b in system]
        body["systemInstruction"] = {"parts": [{"text": t} for t in blocks]}
    if params.get("tools"):
        body["tools"] = [{"functionDeclarations": [
            {"name": t["name"], "description": t.get("description", ""), "parametersJsonSchema": t["input_schema"]}
            for t in params["tools"]
        ]}]
        mode = "NONE" if (params.get("tool_choice") or {}).get("type") == "none" else "AUTO"
        body["toolConfig"] = {"functionCallingConfig": {"mode": mode}}
    body["generationConfig"] = {"maxOutputTokens": min(params.get("max_tokens", 8192), MAX_OUTPUT_TOKENS)}
    return body


# ---------------------------------------------------------------------------- streaming response
class _Stream:
    def __init__(self, client: GeminiClient, model: str, body: dict) -> None:
        self._client, self._model, self._body = client, model, body
        self._response: httpx.Response | None = None
        self._blocks: list[dict] = []
        self._finish = ""
        self._blocked = False
        self._usage: dict = {}
        self._model_version = model
        self._done = False

    async def __aenter__(self) -> _Stream:
        url = f"{API_BASE}/models/{self._model}:streamGenerateContent?alt=sse"
        headers = {"x-goog-api-key": self._client.api_key, "Content-Type": "application/json"}
        self._response = await open_stream(self._client.http, "Gemini", url, headers, self._body,
                                           self._client.max_retries)
        return self

    async def __aexit__(self, *exc) -> bool:
        if self._response is not None:
            await self._response.aclose()
        return False

    def __aiter__(self):
        return self._events()

    async def _events(self):
        assert self._response is not None
        async for line in self._response.aiter_lines():
            if not line.startswith("data:"):
                continue
            try:
                chunk = json.loads(line[5:])
            except json.JSONDecodeError:
                log.warning("Unparseable Gemini SSE line: %.200s", line)
                continue
            for delta in self._absorb(chunk):
                yield SimpleNamespace(type="text", text=delta)
        self._done = True
        if self._finish == "MALFORMED_FUNCTION_CALL":
            # Same recovery as an unparseable tool input on Claude: the runtime re-issues the turn.
            raise ValueError("Gemini trả về function call không hợp lệ")

    def _absorb(self, chunk: dict) -> list[str]:
        self._model_version = chunk.get("modelVersion") or self._model_version
        self._usage = chunk.get("usageMetadata") or self._usage
        if (chunk.get("promptFeedback") or {}).get("blockReason"):
            self._blocked = True
        deltas = []
        for cand in chunk.get("candidates", [])[:1]:
            for part in (cand.get("content") or {}).get("parts", []):
                if part.get("thought"):
                    continue
                sig = part.get("thoughtSignature")
                if "functionCall" in part:
                    fc = part["functionCall"]
                    block = {"type": "tool_use", "id": f"toolu_gem_{uuid.uuid4().hex[:20]}",
                             "name": fc["name"], "input": fc.get("args") or {}}
                    if sig:
                        block["thought_signature"] = sig
                    self._blocks.append(block)
                elif "text" in part:
                    last = self._blocks[-1] if self._blocks else None
                    if last and last["type"] == "text" and not last.get("thought_signature"):
                        last["text"] += part["text"]
                    else:
                        last = {"type": "text", "text": part["text"]}
                        self._blocks.append(last)
                    if sig:
                        last["thought_signature"] = sig
                    if part["text"]:
                        deltas.append(part["text"])
            self._finish = cand.get("finishReason") or self._finish
        return deltas

    async def get_final_message(self) -> BetaMessage:
        if not self._done:
            async for _ in self._events():
                pass
        blocks = [b for b in self._blocks if b["type"] != "text" or b["text"]]
        if any(b["type"] == "tool_use" for b in blocks):
            stop = "tool_use"
        elif self._blocked or self._finish in REFUSAL_REASONS:
            stop = "refusal"
        elif self._finish == "MAX_TOKENS":
            stop = "max_tokens"
        else:
            stop = "end_turn"
        u = self._usage
        cached = u.get("cachedContentTokenCount", 0) or 0
        return BetaMessage.model_validate({
            "id": f"msg_gem_{uuid.uuid4().hex[:20]}", "type": "message", "role": "assistant",
            "model": self._model_version, "content": blocks, "stop_reason": stop, "stop_sequence": None,
            "usage": {
                "input_tokens": max((u.get("promptTokenCount", 0) or 0) - cached, 0),
                "output_tokens": (u.get("candidatesTokenCount", 0) or 0) + (u.get("thoughtsTokenCount", 0) or 0),
                "cache_read_input_tokens": cached,
                "cache_creation_input_tokens": 0,
            },
        })


# ---------------------------------------------------------------------------- client
class GeminiClient:
    """Duck-types `AsyncAnthropic` for `client.beta.messages.stream(**params)`."""

    def __init__(self, api_key: str, default_model: str, max_retries: int = 3,
                 transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.api_key = api_key
        self.default_model = default_model
        self.max_retries = max_retries
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=90.0), transport=transport)
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def resolve_model(self, model: str | None) -> str:
        """Agents configured with a Gemini model keep it; Claude model ids map to the default."""
        if model and model.startswith(("gemini", "gemma")):
            return model
        return self.default_model

    def _stream(self, **params) -> _Stream:
        if not self.api_key:
            raise GeminiError(401, "Chưa cấu hình GOOGLE_API_KEY cho server (xem README).")
        return _Stream(self, self.resolve_model(params.get("model")), to_request(params))
