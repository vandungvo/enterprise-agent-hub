"""LLM client (Anthropic or Gemini, chosen by LLM_PROVIDER), pricing and per-model capabilities."""
from __future__ import annotations

from anthropic import AsyncAnthropic

from .settings import settings

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

# Models that accept server-side refusal fallbacks (`fallbacks: "default"`).
FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


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


def effective_model(model: str) -> str:
    """The model that actually serves an agent configured with `model` under the current provider."""
    if settings.llm_provider == "gemini" and not model.startswith(("gemini", "gemma")):
        return settings.gemini_model
    if settings.llm_provider not in ("anthropic", "gemini") and model.startswith(("claude", "gemini")):
        return _openai_default_model()
    return model


def _openai_default_model() -> str:
    from .openai_compat import DEFAULT_MODELS

    return settings.openai_model or DEFAULT_MODELS.get(settings.llm_provider, "")


_client = None


def get_client():
    """Anthropic: credentials resolve from ANTHROPIC_API_KEY, ANTHROPIC_AUTH_TOKEN or an `ant auth login` profile.
    Gemini: GOOGLE_API_KEY (or GEMINI_API_KEY).
    OpenAI-compatible (groq, ollama, lmstudio, openrouter, openai): OPENAI_API_KEY / GROQ_API_KEY, OPENAI_BASE_URL."""
    global _client
    if _client is None:
        provider = settings.llm_provider
        if provider == "gemini":
            from .gemini import GeminiClient

            _client = GeminiClient(api_key=settings.google_api_key, default_model=settings.gemini_model)
        elif provider != "anthropic":
            from .openai_compat import BASE_URLS, PROVIDERS, OpenAICompatClient

            if provider not in PROVIDERS:
                from .providers import ProviderError

                # not ValueError: the runtime treats ValueError as a retryable tool-input parse error
                raise ProviderError(400, f"LLM_PROVIDER không hợp lệ: {provider!r} "
                                         f"(anthropic, gemini, {', '.join(sorted(PROVIDERS))})")
            _client = OpenAICompatClient(base_url=settings.openai_base_url or BASE_URLS[provider],
                                         api_key=settings.openai_api_key, default_model=_openai_default_model(),
                                         max_tokens=settings.openai_max_tokens, provider_name=provider.capitalize())
        else:
            _client = AsyncAnthropic(max_retries=3)
    return _client
