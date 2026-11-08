"""Gemini adapter: request translation and a full runtime loop over a mocked SSE endpoint."""
import asyncio
import json

import httpx

from app.gemini import DUMMY_SIGNATURE, GeminiClient, to_contents, to_request
from app.orchestrator import AgentRuntime
from app.registry import get_platform
from app.tools import ToolContext
from tests.helpers import P


def _sse(*chunks: dict) -> bytes:
    return "".join(f"data: {json.dumps(c, ensure_ascii=False)}\r\n\r\n" for c in chunks).encode()


def _chunk(parts, finish=None, usage=None):
    cand = {"content": {"role": "model", "parts": parts}}
    if finish:
        cand["finishReason"] = finish
    out = {"candidates": [cand], "modelVersion": "gemini-test"}
    if usage:
        out["usageMetadata"] = usage
    return out


class _Server:
    """Scripted streamGenerateContent endpoint; records every request body."""

    def __init__(self, script: list[bytes | tuple[int, dict]]):
        self.script = list(script)
        self.requests: list[dict] = []
        self.urls: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(json.loads(request.content))
        self.urls.append(str(request.url))
        assert request.headers["x-goog-api-key"] == "test-key"
        item = self.script.pop(0)
        if isinstance(item, tuple):
            return httpx.Response(item[0], json=item[1])
        return httpx.Response(200, content=item, headers={"content-type": "text/event-stream"})


def _client(server: _Server) -> GeminiClient:
    return GeminiClient("test-key", "gemini-default", max_retries=1, transport=httpx.MockTransport(server))


def _ctx(key, agent):
    pl = get_platform()
    return ToolContext(user=P(key), platform=pl, agent=pl.agents[agent], conversation_id=None)


async def _collect(runtime, agent, messages, ctx):
    return [ev async for ev in runtime.run(agent, messages, ctx)]


def test_history_translation_resolves_names_and_signatures():
    messages = [
        {"role": "user", "content": "Phiếu lương của tôi?"},
        {"role": "assistant", "content": [
            {"type": "text", "text": "Để tôi xem."},
            {"type": "tool_use", "id": "t1", "name": "get_payslip", "input": {}, "thought_signature": "SIG"},
            {"type": "tool_use", "id": "t2", "name": "search_knowledge", "input": {"query": "lương"}},  # from Claude
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": "net: 20tr", "is_error": False},
            {"type": "tool_result", "tool_use_id": "t2", "content": "TỪ CHỐI", "is_error": True},
        ]},
    ]
    c = to_contents(messages)
    assert [x["role"] for x in c] == ["user", "model", "user"]
    calls = c[1]["parts"][1:]
    assert calls[0] == {"functionCall": {"name": "get_payslip", "args": {}}, "thoughtSignature": "SIG"}
    assert calls[1]["thoughtSignature"] == DUMMY_SIGNATURE
    assert c[2]["parts"][0]["functionResponse"] == {"name": "get_payslip", "response": {"result": "net: 20tr"}}
    assert c[2]["parts"][1]["functionResponse"] == {"name": "search_knowledge", "response": {"error": "TỪ CHỐI"}}


def test_request_maps_system_tools_and_tool_choice():
    body = to_request({
        "model": "claude-opus-5-5", "max_tokens": 200_000, "system": [{"type": "text", "text": "A"}, {"type": "text", "text": "B"}],
        "messages": [{"role": "user", "content": "x"}], "cache_control": {"type": "ephemeral"},
        "tools": [{"name": "t", "description": "d", "input_schema": {"type": "object", "properties": {}},
                   "eager_input_streaming": True}],
        "tool_choice": {"type": "none"}, "output_config": {"effort": "high"},
    })
    assert body["systemInstruction"] == {"parts": [{"text": "A"}, {"text": "B"}]}
    assert body["tools"][0]["functionDeclarations"][0] == {
        "name": "t", "description": "d", "parametersJsonSchema": {"type": "object", "properties": {}}}
    assert body["toolConfig"]["functionCallingConfig"]["mode"] == "NONE"
    assert body["generationConfig"]["maxOutputTokens"] == 65_536
    assert set(body) == {"contents", "systemInstruction", "tools", "toolConfig", "generationConfig"}


def test_runtime_runs_router_delegation_and_denied_tool_on_gemini():
    usage = {"promptTokenCount": 1000, "candidatesTokenCount": 50, "thoughtsTokenCount": 30,
             "cachedContentTokenCount": 400}
    server = _Server([
        (503, {"error": {"code": 503, "message": "overloaded"}}),  # retried transparently
        _sse(_chunk([{"functionCall": {"name": "delegate_to_agent",
                                       "args": {"agent_id": "people", "task": "Xem lương manager.alpha"}},
                      "thoughtSignature": "SIG-ROUTER"}], "STOP", usage)),
        _sse(_chunk([{"functionCall": {"name": "get_payslip", "args": {"employee": "manager.alpha@saomai.vn"}},
                      "thoughtSignature": "SIG-PEOPLE"}], "STOP", usage)),
        _sse(_chunk([{"text": "Bạn không có "}]), _chunk([{"text": "quyền xem."}], "STOP", usage)),
        _sse(_chunk([{"thought": True, "text": "nghĩ..."}, {"text": "Không được phép xem lương người khác."}],
                    "STOP", usage)),
    ])
    pl = get_platform()
    ctx = _ctx("dev.alpha", "router")
    messages = [{"role": "user", "content": "Lương của manager.alpha?"}]
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), pl.agents["router"], messages, ctx))

    end = [e for e in events if e["type"] == "agent_end" and e["depth"] == 0][0]
    assert end["status"] == "ok" and end["text"] == "Không được phép xem lương người khác."
    denied = next(e for e in events if e["type"] == "tool_result" and e["tool"] == "get_payslip")
    assert denied["is_error"] and denied["preview"].startswith("TỪ CHỐI TRUY CẬP")
    streamed = "".join(e["text"] for e in events if e["type"] == "text" and e["depth"] == 1)
    assert streamed == "Bạn không có quyền xem."

    # Claude model id in platform.yaml maps to the configured Gemini default
    assert all("/models/gemini-default:streamGenerateContent" in u for u in server.urls)
    # router's second call replays its function call with the signature, then the specialist's answer
    second = server.requests[-1]["contents"]
    assert second[1]["parts"][0]["thoughtSignature"] == "SIG-ROUTER"
    assert second[2]["parts"][0]["functionResponse"]["name"] == "delegate_to_agent"
    assert "Bạn không có quyền xem." in second[2]["parts"][0]["functionResponse"]["response"]["result"]
    # specialist's denial went back to Gemini as an error response
    people_followup = server.requests[3]["contents"]
    assert "error" in people_followup[-1]["parts"][0]["functionResponse"]["response"]
    # persisted history stays in Anthropic format
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]
    assert messages[1]["content"][0]["type"] == "tool_use"


def test_safety_block_and_http_error_are_reported():
    pl = get_platform()
    server = _Server([_sse(_chunk([], "PROHIBITED_CONTENT"))])
    ctx = _ctx("dev.alpha", "people")
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    assert events[-1]["status"] == "refusal"

    server = _Server([(403, {"error": {"code": 403, "message": "billing required"}})])
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), pl.agents["people"],
                                  [{"role": "user", "content": "x"}], ctx))
    assert events[-1]["status"] == "error" and "403" in events[-1]["text"] and "billing required" in events[-1]["text"]
