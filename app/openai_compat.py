"""OpenAI-compatible Chat Completions backend (Groq, Ollama, LM Studio, llama.cpp, vLLM, OpenRouter, ...)
behind the subset of the AsyncAnthropic interface the runtime uses.

    client.beta.messages.stream(**params)  ──▶  POST {base_url}/chat/completions  (stream: true)
        async for event in stream          ◀──  {"type": "text", "text": ...} per content delta
        await stream.get_final_message()   ◀──  BetaMessage (text / tool_use blocks, stop_reason, usage)

Mapping:
    system blocks          → one "system" message
    assistant tool_use     → assistant.tool_calls[] (arguments as a JSON string)
    user tool_result       → one "tool" message per result (tool_call_id)
    tools[].input_schema   → tools[].function.parameters
    tool_choice none|auto  → "none" | "auto"
    finish_reason          → stop_reason (tool_calls→tool_use, length→max_tokens, content_filter→refusal)

Anthropic-only params (cache_control, output_config/effort, betas, fallbacks) are ignored. Reasoning
deltas (`reasoning`, `reasoning_content`) are not shown or stored.
"""
from __future__ import annotations

import json
import logging
import uuid
from types import SimpleNamespace
from typing import Any

import httpx
from anthropic.types.beta import BetaMessage

from .providers import ProviderError, open_stream

log = logging.getLogger("agenthub.openai_compat")

# Default endpoints for LLM_PROVIDER aliases; OPENAI_BASE_URL overrides.
BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "ollama": "http://localhost:11434/v1",
    "lmstudio": "http://localhost:1234/v1",
    "openrouter": "https://openrouter.ai/api/v1",
    "openai": "https://api.openai.com/v1",
}
PROVIDERS = set(BASE_URLS)
DEFAULT_MODELS = {"groq": "openai/gpt-oss-120b", "ollama": "qwen3:4b", "openai": "gpt-5-mini"}


# ---------------------------------------------------------------------------- request conversion
def _text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
    return json.dumps(content, ensure_ascii=False, default=str)


def to_messages(system: Any, messages: list[dict]) -> list[dict]:
    out: list[dict] = []
    if system:
        blocks = [system] if isinstance(system, str) else [b["text"] for b in system]
        out.append({"role": "system", "content": "\n\n".join(blocks)})
    for m in messages:
        content = m["content"]
        if isinstance(content, str):
            out.append({"role": m["role"], "content": content})
            continue
        if m["role"] == "assistant":
            text = "".join(b["text"] for b in content if b.get("type") == "text")
            calls = [{"id": b["id"], "type": "function",
                      "function": {"name": b["name"], "arguments": json.dumps(b.get("input") or {}, ensure_ascii=False)}}
                     for b in content if b.get("type") == "tool_use"]
            msg: dict[str, Any] = {"role": "assistant", "content": text or (None if calls else "")}
            if calls:
                msg["tool_calls"] = calls
            out.append(msg)
            continue
        # user turn: tool results first (they must directly follow the assistant tool_calls), then any text
        for b in content:
            if b.get("type") == "tool_result":
                out.append({"role": "tool", "tool_call_id": b["tool_use_id"], "content": _text_of(b.get("content"))})
        text = "\n".join(b["text"] for b in content if b.get("type") == "text" and b.get("text"))
        if text:
            out.append({"role": "user", "content": text})
    return out


def to_request(params: dict, model: str, max_tokens_cap: int) -> dict:
    body: dict[str, Any] = {
        "model": model,
        "messages": to_messages(params.get("system"), params["messages"]),
        "max_tokens": min(params.get("max_tokens", max_tokens_cap), max_tokens_cap),
        "stream": True,
        "stream_options": {"include_usage": True},
    }
    if params.get("tools"):
        body["tools"] = [{"type": "function", "function": {
            "name": t["name"], "description": t.get("description", ""), "parameters": t["input_schema"]}}
            for t in params["tools"]]
        body["tool_choice"] = "none" if (params.get("tool_choice") or {}).get("type") == "none" else "auto"
    return body


# ---------------------------------------------------------------------------- streaming response
class _Stream:
    def __init__(self, client: "OpenAICompatClient", body: dict) -> None:
        self._client, self._body = client, body
        self._response: httpx.Response | None = None
        self._text: list[str] = []
        self._calls: dict[int, dict] = {}
        self._finish = ""
        self._usage: dict = {}
        self._model = body["model"]
        self._done = False

    async def __aenter__(self) -> "_Stream":
        headers = {"Content-Type": "application/json"}
        if self._client.api_key:
            headers["Authorization"] = f"Bearer {self._client.api_key}"
        self._response = await open_stream(self._client.http, self._client.provider_name,
                                           f"{self._client.base_url}/chat/completions", headers, self._body,
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
            data = line[5:].strip()
            if data == "[DONE]":
                break
            try:
                chunk = json.loads(data)
            except json.JSONDecodeError:
                log.warning("Unparseable SSE line: %.200s", line)
                continue
            if "error" in chunk:  # some servers report mid-stream errors as a data event
                err = chunk["error"]
                raise ProviderError(502, err.get("message", str(err)) if isinstance(err, dict) else str(err))
            delta = self._absorb(chunk)
            if delta:
                yield SimpleNamespace(type="text", text=delta)
        self._done = True

    def _absorb(self, chunk: dict) -> str:
        self._model = chunk.get("model") or self._model
        usage = chunk.get("usage") or (chunk.get("x_groq") or {}).get("usage")
        if usage:
            self._usage = usage
        text = ""
        for choice in chunk.get("choices") or []:
            if choice.get("index", 0) != 0:
                continue
            delta = choice.get("delta") or {}
            if delta.get("content"):
                text += delta["content"]
            for tc in delta.get("tool_calls") or []:
                slot = self._calls.setdefault(tc.get("index", len(self._calls)), {"id": "", "name": "", "args": ""})
                fn = tc.get("function") or {}
                slot["id"] = tc.get("id") or slot["id"]
                slot["name"] += fn.get("name") or ""
                args = fn.get("arguments")
                slot["args"] += args if isinstance(args, str) else (json.dumps(args) if args else "")
            self._finish = choice.get("finish_reason") or self._finish
        if text:
            self._text.append(text)
        return text

    async def get_final_message(self) -> BetaMessage:
        if not self._done:
            async for _ in self._events():
                pass
        blocks: list[dict] = []
        text = "".join(self._text)
        if text:
            blocks.append({"type": "text", "text": text})
        for _, call in sorted(self._calls.items()):
            try:
                args = json.loads(call["args"]) if call["args"].strip() else {}
            except json.JSONDecodeError as exc:
                # Same recovery as an unparseable tool input on Claude: the runtime re-issues the turn.
                raise ValueError(f"Tool arguments không phải JSON hợp lệ: {call['args'][:200]}") from exc
            blocks.append({"type": "tool_use", "id": call["id"] or f"call_{uuid.uuid4().hex[:20]}",
                           "name": call["name"], "input": args if isinstance(args, dict) else {"value": args}})
        if any(b["type"] == "tool_use" for b in blocks):
            stop = "tool_use"
        elif self._finish == "length":
            stop = "max_tokens"
        elif self._finish == "content_filter":
            stop = "refusal"
        else:
            stop = "end_turn"
        u = self._usage
        cached = ((u.get("prompt_tokens_details") or {}).get("cached_tokens") or 0)
        return BetaMessage.model_validate({
            "id": f"msg_oai_{uuid.uuid4().hex[:20]}", "type": "message", "role": "assistant",
            "model": self._model, "content": blocks, "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": max((u.get("prompt_tokens") or 0) - cached, 0),
                      "output_tokens": u.get("completion_tokens") or 0,
                      "cache_read_input_tokens": cached, "cache_creation_input_tokens": 0},
        })


# ---------------------------------------------------------------------------- client
class OpenAICompatClient:
    """Duck-types `AsyncAnthropic` for `client.beta.messages.stream(**params)`."""

    def __init__(self, base_url: str, api_key: str, default_model: str, max_tokens: int = 4096,
                 max_retries: int = 4, provider_name: str = "OpenAI-compatible",
                 transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.default_model = default_model
        self.max_tokens = max_tokens
        self.max_retries = max_retries
        self.provider_name = provider_name
        self.http = httpx.AsyncClient(timeout=httpx.Timeout(30.0, read=300.0), transport=transport)
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def resolve_model(self, model: str | None) -> str:
        """Agents configured with a Claude/Gemini id use the default; any other id is passed through."""
        if not model or model.startswith(("claude", "gemini")):
            return self.default_model
        return model

    def _stream(self, **params) -> _Stream:
        model = self.resolve_model(params.get("model"))
        if not model:
            raise ProviderError(400, "Chưa cấu hình OPENAI_MODEL cho server (xem README).")
        return _Stream(self, to_request(params, model, self.max_tokens))
