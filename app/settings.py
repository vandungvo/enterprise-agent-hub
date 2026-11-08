"""Runtime settings, read from environment variables (or a .env file)."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


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
    data_dir: Path = Path(os.getenv("AGENTHUB_DATA_DIR", ROOT / "data"))
    config_path: Path = Path(os.getenv("AGENTHUB_CONFIG", ROOT / "config" / "platform.yaml"))
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

    @property
    def app_db_url(self) -> str:
        return f"sqlite:///{self.data_dir / 'agenthub.db'}"

    @property
    def business_db_path(self) -> Path:
        return self.data_dir / "business.db"

    @property
    def uploads_dir(self) -> Path:
        return self.data_dir / "uploads"


settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
settings.uploads_dir.mkdir(parents=True, exist_ok=True)
