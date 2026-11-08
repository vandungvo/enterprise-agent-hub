# Build & Installation Instructions

## 1. Prerequisites
- Python 3.12 hoặc mới hơn (Vercel chạy 3.12; CI kiểm thử 3.12 và 3.13).
- Tùy chọn: PostgreSQL 16 (production-like), hoặc Docker để chạy `docker compose`.

## 2. Cài đặt

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements-dev.txt   # runtime (đã pin) + pytest, ruff
copy .env.example .env                                 # điền LLM_PROVIDER và API key
```

## 3. Biến môi trường cốt lõi

| Biến | Ý nghĩa |
|---|---|
| `LLM_PROVIDER` | `anthropic` (mặc định) \| `gemini` \| `groq` \| `ollama` \| `lmstudio` \| `openrouter` \| `openai` |
| `ANTHROPIC_API_KEY` / `GOOGLE_API_KEY` / `GROQ_API_KEY` / `OPENAI_API_KEY` | Theo provider |
| `DATABASE_URL` | Trống = SQLite `data/agenthub.db`; production: `postgresql://...` |
| `AGENTHUB_SECRET` | Khóa HMAC ký token đăng nhập (bắt buộc nên đặt ở production) |
| `LOG_FORMAT` / `LOG_LEVEL` | `text` \| `json`; `INFO` |
| `CRON_SECRET` | Bật `/api/internal/maintenance` cho scheduler |

Danh sách đầy đủ: `.env.example` và README.

## 4. Khởi động

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --reload --port 8000
```

Lúc khởi động, app tự chạy **Alembic migrations** rồi seed dữ liệu mẫu (idempotent, có khóa khi nhiều instance cùng khởi động). Không cần bước seed riêng (`app/bootstrap.py` chạy trong lifespan). Kiểm tra: `GET /api/health`.

Production-like bằng container: `docker compose up --build` (app + PostgreSQL 16).

## 5. Làm việc với schema

```powershell
# sau khi sửa model trong app/models.py hoặc bảng trong app/hris/schema.py:
.\.venv\Scripts\alembic revision --autogenerate -m "mo ta thay doi"   # sinh migrations/versions/NNNN_*.py, review rồi commit
.\.venv\Scripts\alembic upgrade head                                 # áp dụng (app cũng tự làm khi khởi động)
.\.venv\Scripts\alembic current
```

`tests/test_migrations.py` fail nếu model và migration lệch nhau.
