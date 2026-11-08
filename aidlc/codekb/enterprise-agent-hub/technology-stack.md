# Technology Stack & Environment

## 1. Programming Languages & Runtime
- **Python**: 3.11+ (Hỗ trợ tốt nhất type hinting, async/await, Pydantic v2).
- **Web Frontend**: HTML5, Vanilla JavaScript ES6+, CSS3 (Zero-build, không phụ thuộc Webpack hay Node.js runtime).

## 2. Frameworks & Core Libraries
- **Web Framework**: FastAPI (>=0.115) - Asynchronous web framework hiệu năng cao.
- **ASGI Server**: Uvicorn (>=0.34) với chuẩn Standard loop (uvloop, httptools).
- **Data Validation & Schemas**: Pydantic (>=2.10) cho request/response models và Pydantic typed tools.
- **ORM & Data Layer**: SQLAlchemy (>=2.0) Core & ORM.
- **Database Engine**:
  - Development / Demo: SQLite (`data/enterprise.db`).
  - Production Target: PostgreSQL 16+ với Row-Level Security (RLS).
- **Configuration**: PyYAML (>=6.0) cho declarative YAML configs.

## 3. NLP, Search & Retrieval
- **Lexical Search**: Custom BM25 implementation tối ưu hóa cho tiếng Việt có dấu và không dấu (`app/rag/text.py`).
- **Dense Embeddings**: FastEmbed (>=0.4) với mô hình `BAAI/bge-small-en-v1.5` hoặc đa ngôn ngữ.
- **Document Processing**: `pypdf` (>=5.0) cho PDF, `python-docx` (>=1.1) cho Word (.docx), `csv` cho dữ liệu bảng.
- **Ranking Fusion**: Reciprocal Rank Fusion (RRF) kết hợp kết quả BM25 và Vector.

## 4. AI & Large Language Models
- **Default Primary Model**: Anthropic Claude (`claude-opus-5-5` / `claude-3-5-sonnet`) qua Messages API, hỗ trợ Prompt Caching và reasoning effort (`low`, `medium`, `high`).
- **Alternative Providers**:
  - Google Gemini API (`gemini-1.5-pro`, `gemini-2.0-flash`) qua `httpx` async client.
  - OpenAI Compatible: Groq, Ollama (Local Self-hosted), LM Studio, OpenRouter.

## 5. Testing & Quality Assurance
- **Test Runner**: Pytest (>=8.0).
- **Async Testing**: `pytest-asyncio` / httpx AsyncClient.
- **Mocking**: `unittest.mock` và `fake_claude.py` để test deterministic không tốn token LLM thật.
