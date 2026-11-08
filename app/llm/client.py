"""LLM client selection (Anthropic, Gemini or OpenAI-compatible, chosen by LLM_PROVIDER) and model capabilities."""
from __future__ import annotations

from anthropic import AsyncAnthropic

from app.core.settings import settings

# Models that accept server-side refusal fallbacks (`fallbacks: "default"`).
FALLBACK_MODELS = {"claude-fable-5-1", "claude-opus-5-5", "claude-opus-5", "claude-sonnet-5-5"}
FALLBACK_BETA = "server-side-fallback-2026-07-01"


def effective_model(model: str) -> str:
    """The model that actually serves an agent configured with `model` under the current provider."""
    if settings.llm_provider == "gemini" and not model.startswith(("gemini", "gemma")):
        return settings.gemini_model
    if settings.llm_provider not in ("anthropic", "gemini") and model.startswith(("claude", "gemini")):
        return _openai_default_model()
    return model


def _openai_default_model() -> str:
    from app.llm.openai_compat import DEFAULT_MODELS

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
            from app.llm.gemini import GeminiClient

            _client = GeminiClient(api_key=settings.google_api_key, default_model=settings.gemini_model)
        elif provider != "anthropic":
            from app.llm.openai_compat import BASE_URLS, PROVIDERS, OpenAICompatClient

            if provider not in PROVIDERS:
                from app.llm.base import ProviderError

                # not ValueError: the runtime treats ValueError as a retryable tool-input parse error
                raise ProviderError(400, f"LLM_PROVIDER không hợp lệ: {provider!r} "
                                         f"(anthropic, gemini, {', '.join(sorted(PROVIDERS))})")
            _client = OpenAICompatClient(base_url=settings.openai_base_url or BASE_URLS[provider],
                                         api_key=settings.openai_api_key, default_model=_openai_default_model(),
                                         max_tokens=settings.openai_max_tokens, provider_name=provider.capitalize())
        else:
            _client = AsyncAnthropic(max_retries=3)
    return _client
