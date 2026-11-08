# Deployment Strategy & Pipeline Specification

## 1. Môi trường hiện tại: Vercel (demo)

- **Production URL**: https://ent-agents.vercel.app (Vercel project `enterprise-agent-hub`).
- **Runtime**: Python Serverless Function. `api/index.py` re-export `app.main:app` (FastAPI ASGI).
- **Routing** (`vercel.json`): rewrite mọi đường dẫn (`/`, `/static/*`, `/api/*`) về `/api/index`, nên FastAPI phục vụ cả API lẫn UI. `includeFiles` đóng gói `app/`, `config/`, `static/`, `seed_docs/`. `maxDuration: 300` cho SSE chat dài.
- **Loại trừ khi upload** (`.vercelignore`): `.venv`, `.env`, `data/`, `tests/`, `aidlc/`.
- **Dữ liệu**: PostgreSQL (Neon qua Vercel Marketplace, biến `DATABASE_URL` do Vercel cấp) dùng chung cho mọi instance: tài khoản, hội thoại, phê duyệt, KB, log và bảng HRIS mẫu (ADR-07). `seed()` chạy trong `lifespan` ở mỗi cold start, có `pg_advisory_lock`; lần đầu tạo dữ liệu (seed cố định `random.Random(2026)`), các lần sau chỉ kiểm tra. Không có `DATABASE_URL` thì rơi về SQLite `/tmp/agenthub` (per-instance, chỉ để thử).
- **Schema**: Alembic migrations chạy tự động lúc khởi động trong cùng khóa với seed (ADR-08); thư mục `migrations/` được đóng gói qua `includeFiles`.
- **Xác thực đa instance**: token đăng nhập stateless ký HMAC (xem ADR-06), nên các instance chạy song song đều xác thực được mà không cần session store chung.

### Biến môi trường (Production)

| Biến | Ghi chú |
|---|---|
| `LLM_PROVIDER` | `groq` (hiện tại) \| `gemini` \| `anthropic` \| ... |
| `GROQ_API_KEY` / `GOOGLE_API_KEY` / `ANTHROPIC_API_KEY` | Theo provider |
| `OPENAI_MODEL`, `GEMINI_MODEL` | Tùy chọn |
| `RAG_EMBEDDINGS` | `none` (fastembed không phù hợp serverless) |
| `DATABASE_URL` | Do Neon integration cấp (dạng `postgres://`, app tự chuyển sang driver psycopg) |
| `AGENTHUB_SECRET` | Khuyến nghị: khóa HMAC cho token; nếu thiếu thì sinh từ các API key LLM |
| `CRON_SECRET` | Bật `/api/internal/maintenance`; Vercel Cron (khai trong `vercel.json`, 03:00 giờ VN hằng ngày) tự gửi kèm |
| `LOG_FORMAT` | `json` khi đẩy log sang log drain |

### Quy trình release

```bash
vercel deploy                                              # 1. preview URL riêng (có Vercel Authentication)
vercel curl /api/health --deployment <preview-url> --yes   # 2. phải trả {"status":"ok"} (Git Bash: MSYS_NO_PATHCONV=1)
vercel --prod                                              # 3. production, alias ent-agents.vercel.app trỏ sang bản mới
```

Dependency: Vercel cài từ `pyproject.toml` (`[project].dependencies`, bằng uv); `requirements.txt` là bản sao cho pip/Docker/CI, test giữ hai nơi khớp nhau.

Thay đổi biến môi trường chỉ có hiệu lực sau lần deploy kế tiếp. Có thể nối repo GitHub để mỗi push lên `main` tự deploy production và mỗi PR có preview.

### Giới hạn đã biết của môi trường demo

- `POST /api/admin/reload` chỉ nạp lại YAML trên instance nhận request; trên Vercel hãy deploy lại sau khi sửa cấu hình.
- Production công khai, mật khẩu demo hiển thị trên trang đăng nhập: dùng API key có giới hạn chi tiêu hoặc bật Deployment Protection.

## 2. Mục tiêu production (Private Cloud / VPC)

Khi lên môi trường doanh nghiệp, dùng `Dockerfile` trong repo (non-root, healthcheck `/api/health`, log JSON) và PostgreSQL dùng chung. Chạy thử production-like: `docker compose up --build`. Nội dung image tương đương:

```dockerfile
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY config/ ./config/
COPY static/ ./static/
COPY seed_docs/ ./seed_docs/
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

- **Dữ liệu dùng chung**: đã dùng PostgreSQL qua `DATABASE_URL` (Neon / Supabase / RDS đều được); HRIS mẫu thay bằng connector thật.
- **Danh tính**: SSO qua OIDC (Azure AD, Google Workspace, Keycloak); đặt `AGENTHUB_SECRET` từ secret manager.
- **Release**: Rolling Update hoặc Blue-Green, tối thiểu 2 replicas. Healthcheck `GET /api/health` (kiểm tra kết nối database, trả 503 khi lỗi).
- **Đổi cấu hình nóng** (`platform.yaml`, `policies.yaml`): `POST /api/admin/reload`, không gián đoạn các stream đang chạy. Với nhiều replica phải gọi trên từng replica hoặc deploy lại.
