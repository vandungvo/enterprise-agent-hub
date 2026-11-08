"""Runtime settings, read from environment variables (or a .env file)."""
from __future__ import annotations

import hashlib
import os
import secrets
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # repo root
IS_VERCEL = bool(os.getenv("VERCEL"))


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader (KEY=VALUE lines); real env vars take precedence."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    # Local files (SQLite fallback, dev session secret). Vercel's filesystem is read-only except /tmp.
    data_dir: Path = Path(os.getenv("AGENTHUB_DATA_DIR") or ("/tmp/agenthub" if IS_VERCEL else ROOT / "data"))
    # One database for platform data AND the demo HRIS. Empty: SQLite file in data_dir (dev / tests).
    # Production / serverless: PostgreSQL, so every instance sees the same users, conversations, approvals.
    database_url_env: str = (os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "").strip()
    db_pool_size: int = int(os.getenv("DB_POOL_SIZE", "3"))
    config_path: Path = Path(os.getenv("AGENTHUB_CONFIG", ROOT / "config" / "platform.yaml"))
    policies_path: Path = Path(os.getenv("AGENTHUB_POLICIES", ROOT / "config" / "policies.yaml"))
    seed_docs_dir: Path = ROOT / "seed_docs"
    static_dir: Path = ROOT / "static"

    # LLM provider: anthropic (Claude) | gemini (Google)
    llm_provider: str = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    google_api_key: str = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY") or ""
    # used for agents whose platform.yaml model is a Claude id; set `model: gemini-...` per agent to override
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    # OpenAI-compatible servers: LLM_PROVIDER=groq | ollama | lmstudio | openrouter | openai
    openai_base_url: str = os.getenv("OPENAI_BASE_URL", "")  # empty: the provider's default endpoint
    openai_api_key: str = os.getenv("OPENAI_API_KEY") or os.getenv("GROQ_API_KEY") or ""
    openai_model: str = os.getenv("OPENAI_MODEL", "")  # empty: the provider's default model
    # completion cap per call; keep it low on free tiers that count it against tokens-per-minute
    openai_max_tokens: int = int(os.getenv("OPENAI_MAX_TOKENS", "4096"))

    # RAG
    embeddings: str = os.getenv("RAG_EMBEDDINGS", "none")  # none | fastembed
    embedding_model: str = os.getenv(
        "RAG_EMBEDDING_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )
    chunk_size: int = int(os.getenv("RAG_CHUNK_SIZE", "900"))  # characters
    chunk_overlap: int = int(os.getenv("RAG_CHUNK_OVERLAP", "150"))

    # Agent runtime
    max_agent_iterations: int = int(os.getenv("AGENT_MAX_ITERATIONS", "8"))
    max_tokens: int = int(os.getenv("AGENT_MAX_TOKENS", "32000"))
    use_fallbacks: bool = os.getenv("AGENT_USE_FALLBACKS", "true").lower() == "true"

    session_hours: int = int(os.getenv("SESSION_HOURS", "12"))
    # conversations that touched restricted data (salary, personal data) are purged after N days
    sensitive_retention_days: int = int(os.getenv("SENSITIVE_RETENTION_DAYS", "30"))
    # in-process org-tree snapshot is refreshed after this many seconds (HRIS changes reach every instance)
    org_cache_ttl: int = int(os.getenv("ORG_CACHE_TTL", "300"))

    # Operations
    log_level: str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_format: str = os.getenv("LOG_FORMAT", "text").lower()  # text | json
    # brute-force protection: N failed sign-ins for one account within the window -> 429 (shared via the DB)
    login_max_failures: int = int(os.getenv("LOGIN_MAX_FAILURES", "10"))
    login_window_minutes: int = int(os.getenv("LOGIN_WINDOW_MINUTES", "15"))
    # protects /api/internal/* (scheduled maintenance); Vercel Cron sends it as "Authorization: Bearer ..."
    cron_secret: str = os.getenv("CRON_SECRET", "")

    @cached_property
    def session_secret(self) -> bytes:
        """HMAC key for login tokens; must be identical on every server instance.
        AGENTHUB_SECRET if set; else derived from the configured LLM keys (secret and shared across instances);
        else a random key persisted in the data dir (single-machine dev)."""
        if os.getenv("AGENTHUB_SECRET"):
            return os.environ["AGENTHUB_SECRET"].encode()
        keys = [os.getenv(k, "") for k in ("ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "GEMINI_API_KEY",
                                            "OPENAI_API_KEY", "GROQ_API_KEY")]
        if any(keys):
            return hashlib.sha256(("agenthub-session-v1\0" + "\0".join(keys)).encode()).digest()
        path = self.data_dir / ".session_secret"
        if not path.exists():
            path.write_text(secrets.token_hex(32), encoding="utf-8")
        return path.read_text(encoding="utf-8").strip().encode()

    @property
    def database_url(self) -> str:
        url = self.database_url_env
        if not url:
            return f"sqlite:///{(self.data_dir / 'agenthub.db').as_posix()}"
        # Neon / Vercel / Heroku hand out postgres:// or postgresql:// - pin the psycopg (v3) driver.
        for prefix in ("postgres://", "postgresql://"):
            if url.startswith(prefix):
                return "postgresql+psycopg://" + url[len(prefix):]
        return url

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


    def validate(self) -> list[str]:
        """Configuration errors that must stop the process (fail fast instead of failing on first use)."""
        errors = []
        if self.log_format not in ("text", "json"):
            errors.append(f"LOG_FORMAT must be text or json, got {self.log_format!r}")
        if self.log_level not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            errors.append(f"LOG_LEVEL is invalid: {self.log_level!r}")
        if not 0 <= self.chunk_overlap < self.chunk_size:
            errors.append("RAG_CHUNK_OVERLAP must be >= 0 and smaller than RAG_CHUNK_SIZE")
        if self.embeddings not in ("none", "fastembed"):
            errors.append(f"RAG_EMBEDDINGS must be none or fastembed, got {self.embeddings!r}")
        for name in ("max_agent_iterations", "max_tokens", "session_hours", "db_pool_size", "login_max_failures",
                     "login_window_minutes"):
            if getattr(self, name) < 1:
                errors.append(f"{name.upper()} must be >= 1")
        return errors

    def warnings(self) -> list[str]:
        out = []
        if IS_VERCEL and self.is_sqlite:
            out.append("No DATABASE_URL on Vercel: using per-instance SQLite in /tmp - data is NOT shared or kept")
        if IS_VERCEL and not os.getenv("AGENTHUB_SECRET"):
            out.append("AGENTHUB_SECRET is not set: login tokens are signed with a key derived from the LLM API keys")
        return out


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
