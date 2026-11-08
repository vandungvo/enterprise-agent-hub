"""Price table (USD per 1M tokens) and cost estimation for the usage dashboard."""
from __future__ import annotations

# USD per 1M tokens: (input, output, cache_read, cache_write_5m)
PRICING = {
    "claude-fable-5-1": (10.0, 50.0, 0.25, 12.5),
    "claude-opus-5-5": (4.0, 20.0, 0.20, 5.0),
    "claude-sonnet-5-5": (2.0, 10.0, 0.20, 2.5),
    "claude-haiku-5-5": (0.10, 0.50, 0.01, 0.125),
    # Gemini: list prices for prompts <= 200k tokens; cost is an estimate (check Google's pricing page)
    "gemini-2.5-pro": (1.25, 10.0, 0.125, 0.0),
    "gemini-2.5-flash": (0.30, 2.50, 0.03, 0.0),
    "gemini-2.5-flash-lite": (0.10, 0.40, 0.01, 0.0),
}
GEMINI_DEFAULT_PRICE = PRICING["gemini-2.5-flash"]

FREE = (0.0, 0.0, 0.0, 0.0)


def _price(model: str):
    if model in PRICING:
        return PRICING[model]
    if model.startswith(("gemini", "gemma")):
        return next((p for name, p in PRICING.items() if model.startswith(name + "-")), GEMINI_DEFAULT_PRICE)
    if model.startswith("claude"):
        return PRICING["claude-opus-5-5"]
    return FREE  # local / free-tier OpenAI-compatible models: no price table, cost shown as 0


def estimate_cost(model: str, usage) -> float:
    inp, out, cread, cwrite = _price(model or "")
    return (
        (usage.input_tokens or 0) * inp
        + (usage.output_tokens or 0) * out
        + (getattr(usage, "cache_read_input_tokens", 0) or 0) * cread
        + (getattr(usage, "cache_creation_input_tokens", 0) or 0) * cwrite
    ) / 1_000_000
