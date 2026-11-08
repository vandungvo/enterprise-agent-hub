"""A scripted stand-in for AsyncAnthropic so the runtime can be tested offline."""
from __future__ import annotations

import itertools
from types import SimpleNamespace

from anthropic.types.beta import BetaMessage

_ids = itertools.count(1)


def text(t: str) -> dict:
    return {"type": "text", "text": t}


def tool(name: str, **inp) -> dict:
    return {"type": "tool_use", "id": f"toolu_{next(_ids):04d}", "name": name, "input": inp}


class _Stream:
    def __init__(self, message: BetaMessage):
        self.message = message

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def __aiter__(self):
        async def gen():
            for block in self.message.content:
                if block.type == "text":
                    yield SimpleNamespace(type="text", text=block.text)
        return gen()

    async def get_final_message(self):
        return self.message


class FakeClaude:
    """`script` is a list of content-block lists, consumed one per model call."""

    def __init__(self, script: list[list[dict]]):
        self.script = list(script)
        self.calls: list[dict] = []
        self.beta = SimpleNamespace(messages=SimpleNamespace(stream=self._stream))

    def _stream(self, **params):
        self.calls.append(params)
        content = self.script.pop(0)
        stop = "tool_use" if any(b["type"] == "tool_use" for b in content) else "end_turn"
        msg = BetaMessage.model_validate({
            "id": f"msg_{next(_ids)}", "type": "message", "role": "assistant", "model": params["model"],
            "content": content, "stop_reason": stop, "stop_sequence": None,
            "usage": {"input_tokens": 100, "output_tokens": 20, "cache_read_input_tokens": 0,
                      "cache_creation_input_tokens": 0},
        })
        return _Stream(msg)
