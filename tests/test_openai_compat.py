"""OpenAI-compatible adapter (Groq / Ollama / ...): translation and a full runtime loop over mocked SSE."""
import asyncio
import json

import httpx

from app.openai_compat import OpenAICompatClient, to_messages, to_request
from app.orchestrator import AgentRuntime
from app.registry import get_platform
from app.tools import ToolContext
from tests.helpers import P


def _sse(*chunks: dict) -> bytes:
    lines = [f"data: {json.dumps(c, ensure_ascii=False)}\n\n" for c in chunks] + ["data: [DONE]\n\n"]
    return "".join(lines).encode()


def _delta(delta=None, finish=None, **extra):
    return {"model": "test-model", "choices": [{"index": 0, "delta": delta or {}, "finish_reason": finish}], **extra}


def _call(name, args, cid="call_1"):
    """A tool call streamed in two fragments, as Groq / Ollama do."""
    raw = json.dumps(args, ensure_ascii=False)
    return [
        _delta({"tool_calls": [{"index": 0, "id": cid, "type": "function", "function": {"name": name, "arguments": raw[:5]}}]}),
        _delta({"tool_calls": [{"index": 0, "function": {"arguments": raw[5:]}}]}, "tool_calls",
               x_groq={"usage": {"prompt_tokens": 900, "completion_tokens": 40}}),
    ]


class _Server:
    def __init__(self, script):
        self.script = list(script)
        self.requests: list[dict] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "http://llm.test/v1/chat/completions"
        assert request.headers["authorization"] == "Bearer k"
        self.requests.append(json.loads(request.content))
        item = self.script.pop(0)
        if isinstance(item, tuple):
            status, body, headers = item
            return httpx.Response(status, json=body, headers=headers)
        return httpx.Response(200, content=item, headers={"content-type": "text/event-stream"})


def _client(server):
    return OpenAICompatClient("http://llm.test/v1/", "k", "default-model", max_tokens=4096, max_retries=2,
                              provider_name="Test", transport=httpx.MockTransport(server))


def _ctx(key, agent):
    pl = get_platform()
    return ToolContext(user=P(key), platform=pl, agent=pl.agents[agent], conversation_id=None)


async def _collect(runtime, agent, messages, ctx):
    return [ev async for ev in runtime.run(agent, messages, ctx)]


def test_history_translation():
    out = to_messages([{"type": "text", "text": "A"}, {"type": "text", "text": "B"}], [
        {"role": "user", "content": "hỏi"},
        {"role": "assistant", "content": [
            {"type": "text", "text": "để tôi xem"},
            {"type": "tool_use", "id": "t1", "name": "get_payslip", "input": {"period": "2026-10"}},
            {"type": "tool_use", "id": "t2", "name": "search_knowledge", "input": {}},
        ]},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "t1", "content": "net: 20tr", "is_error": False},
            {"type": "tool_result", "tool_use_id": "t2", "content": [{"type": "text", "text": "TỪ CHỐI"}], "is_error": True},
        ]},
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t3", "name": "x", "input": {}}]},
    ])
    assert out[0] == {"role": "system", "content": "A\n\nB"}
    assert out[2]["content"] == "để tôi xem"
    assert out[2]["tool_calls"][0]["function"] == {"name": "get_payslip", "arguments": '{"period": "2026-10"}'}
    assert out[3] == {"role": "tool", "tool_call_id": "t1", "content": "net: 20tr"}
    assert out[4] == {"role": "tool", "tool_call_id": "t2", "content": "TỪ CHỐI"}
    assert out[5]["content"] is None and out[5]["tool_calls"][0]["id"] == "t3"


def test_request_caps_tokens_and_maps_tool_choice():
    body = to_request({"model": "claude-opus-5-5", "max_tokens": 32000, "messages": [{"role": "user", "content": "x"}],
                       "tools": [{"name": "t", "description": "d", "input_schema": {"type": "object"},
                                  "eager_input_streaming": True}],
                       "tool_choice": {"type": "none"}, "cache_control": {"type": "ephemeral"}}, "m", 4096)
    assert body["max_tokens"] == 4096 and body["model"] == "m" and body["tool_choice"] == "none"
    assert body["tools"] == [{"type": "function", "function": {"name": "t", "description": "d",
                                                               "parameters": {"type": "object"}}}]
    assert "cache_control" not in body


def test_runtime_router_delegation_denial_and_rate_limit_retry():
    server = _Server([
        (429, {"error": {"message": "Rate limit reached for tokens per minute"}}, {"retry-after": "0.5"}),
        _sse(*_call("delegate_to_agent", {"agent_id": "people", "task": "Xem lương manager.alpha"})),
        _sse(*_call("get_payslip", {"employee": "manager.alpha@saomai.vn"}, "call_2")),
        _sse(_delta({"reasoning": "nghĩ..."}), _delta({"content": "Bạn không có "}),
             _delta({"content": "quyền xem."}, "stop"), {"choices": [], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}),
        _sse(_delta({"content": "Không được phép xem lương người khác."}, "stop")),
    ])
    pl = get_platform()
    ctx = _ctx("dev.alpha", "router")
    messages = [{"role": "user", "content": "Lương của manager.alpha?"}]
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), pl.agents["router"], messages, ctx))

    end = [e for e in events if e["type"] == "agent_end" and e["depth"] == 0][0]
    assert end["status"] == "ok" and end["text"] == "Không được phép xem lương người khác."
    denied = next(e for e in events if e["type"] == "tool_result" and e["tool"] == "get_payslip")
    assert denied["is_error"] and denied["preview"].startswith("TỪ CHỐI TRUY CẬP")
    assert "".join(e["text"] for e in events if e["type"] == "text" and e["depth"] == 1) == "Bạn không có quyền xem."
    assert all(r["model"] == "default-model" for r in server.requests)  # Claude ids map to the default
    last = server.requests[-1]["messages"]
    assert last[-2]["tool_calls"][0]["id"] == "call_1"
    assert last[-1]["role"] == "tool" and last[-1]["tool_call_id"] == "call_1"
    assert [m["role"] for m in messages] == ["user", "assistant", "user", "assistant"]


def test_bad_tool_json_is_retried_and_http_errors_reported():
    ctx = _ctx("dev.alpha", "people")
    broken = _delta({"tool_calls": [{"index": 0, "id": "c", "function": {"name": "get_payslip", "arguments": '{"a": '}}]},
                    "tool_calls")
    server = _Server([_sse(broken), _sse(_delta({"content": "ok"}, "stop"))])
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    assert events[-1]["status"] == "ok" and len(server.requests) == 2

    server = _Server([(401, {"error": {"message": "Invalid API Key"}}, {})])
    events = asyncio.run(_collect(AgentRuntime(client=_client(server)), ctx.agent, [{"role": "user", "content": "x"}], ctx))
    assert events[-1]["status"] == "error" and "401" in events[-1]["text"] and "Invalid API Key" in events[-1]["text"]
