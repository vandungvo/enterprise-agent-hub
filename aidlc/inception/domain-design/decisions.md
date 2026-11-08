# Architecture Decision Records (ADR Log)

## ADR-01: Data-Tier Deterministic ABAC vs. Prompt-Tier Guardrails
- **Trạng thái**: Accepted
- **Bối cảnh**: LLM có thể bị đánh lừa qua các kỹ thuật Jailbreak hoặc Indirect Prompt Injection nếu việc phân quyền dựa vào system prompt.
- **Quyết định**: Toàn bộ quyết định phân quyền dữ liệu (Policy Decision Point) và thực thi (Policy Enforcement Point) nằm ở tầng mã Python trước khi truy vấn SQL. Model chỉ nhận được dữ liệu hợp lệ.
- **Hệ quả**: Triệt tiêu hoàn toàn nguy cơ rò rỉ dữ liệu mật qua prompt injection; tăng nhẹ thời gian xử lý (dưới 50ms per call) nhưng đảm bảo an toàn tuyệt đối.

## ADR-02: Multi-Agent Router Delegation vs. Monolithic Agent Prompt
- **Trạng thái**: Accepted
- **Bối cảnh**: Hệ thống có quá nhiều nghiệp vụ đa dạng (HR, Lương, Phép, Ngân sách, IT Helpdesk). Một prompt nguyên khối sẽ quá tải context window và làm giảm độ chính xác khi gọi 16 công cụ cùng lúc.
- **Quyết định**: Sử dụng Router Agent làm cửa tiếp nhận, phân tích ý định và ủy quyền cho 5 Agent chuyên môn qua tool `delegate_to_agent`.
- **Hệ quả**: Giảm kích thước context window, cô lập danh sách công cụ theo từng agent, tối ưu chi phí token qua Prompt Caching.

## ADR-03: Hybrid BM25 + Dense Embeddings with RRF vs. Pure Vector Search
- **Trạng thái**: Accepted
- **Bối cảnh**: Văn bản nội bộ doanh nghiệp bằng tiếng Việt thường chứa nhiều mã số văn bản, từ khóa chuyên ngành, số quyết định viết tắt mà mô hình vector embedding thông thường dễ bỏ sót.
- **Quyết định**: Kết hợp Lexical BM25 (xử lý tiếng Việt có dấu/không dấu) với Dense Vector Embeddings (FastEmbed) và trộn kết quả bằng Reciprocal Rank Fusion (RRF).
- **Hệ quả**: Độ chính xác tìm kiếm (recall & precision) cao vượt trội, trích dẫn chuẩn xác văn bản quy định.

## ADR-04: Human-in-the-Loop for Mutating Operations
- **Trạng thái**: Accepted
- **Bối cảnh**: Các hành động nộp đơn nghỉ phép, xin hoàn ứng chi phí tạo tác động trực tiếp đến quyền lợi và ngân sách tập đoàn.
- **Quyết định**: Tool không cập nhật trạng thái cuối cùng ngay lập tức mà tạo một bản ghi `approval_requests` với trạng thái `PENDING`, tự động định tuyến tới người quản lý có thẩm quyền theo quan hệ báo cáo tổ chức.
- **Hệ quả**: Đảm bảo quy trình quản trị doanh nghiệp, phòng chống tự động hóa sai lệch hoặc trục lợi.

## ADR-05: Demo Hosting on Vercel Serverless (Python Function)
- **Trạng thái**: Accepted (2026-11-09), áp dụng cho môi trường demo
- **Bối cảnh**: Cần một URL công khai để demo cho stakeholder mà không phải vận hành máy chủ. Ứng dụng là FastAPI + SQLite, giao diện tĩnh không cần build.
- **Quyết định**: Deploy lên Vercel dưới dạng một Python Serverless Function (`api/index.py` re-export `app.main:app`), `vercel.json` rewrite mọi route về function. Dữ liệu SQLite đặt ở `/tmp/agenthub` và được seed lại ở mỗi cold start.
- **Hệ quả**: Deploy bằng một lệnh (`vercel --prod`), có preview URL cho mỗi bản. Đánh đổi: dữ liệu ghi (hội thoại, phê duyệt, upload, log) là per-instance và mất khi instance bị thu hồi. Production thật cần PostgreSQL + object storage (xem `operation/deployment-pipeline/deployment-strategy.md`).

## ADR-06: Stateless HMAC-Signed Login Tokens vs. DB Session Table
- **Trạng thái**: Accepted (2026-11-09), thay thế bảng `auth_sessions`
- **Bối cảnh**: Trên Vercel, các request song song của cùng một trình duyệt rơi vào nhiều instance, mỗi instance có SQLite riêng. Phiên lưu trong bảng `auth_sessions` chỉ tồn tại ở instance xử lý login, nên các instance khác trả 401 và UI tự đăng xuất ("vào acc CEO bị out ra").
- **Quyết định**: Token = `base64url(JSON{email, exp}).base64url(HMAC-SHA256)`. Khóa lấy từ `AGENTHUB_SECRET`; nếu không có thì dẫn xuất (SHA-256, có domain separation) từ các API key LLM đã cấu hình; local không có key thì dùng file ngẫu nhiên `data/.session_secret`. Token chỉ mang email; Principal vẫn dựng lại từ HRIS ở mỗi request (giữ nguyên invariant "danh tính từ HRIS, không từ client").
- **Hệ quả**: Instance nào cũng xác thực được, không cần session store. Đánh đổi: không thu hồi được từng token riêng lẻ trước hạn (`SESSION_HOURS`, mặc định 12h); thu hồi toàn bộ bằng cách đổi khóa. Test: `tests/test_api.py::test_session_token_is_signed_and_stateless`.

## ADR-07: Shared PostgreSQL for All State (Platform + Demo HRIS) vs. Per-Instance SQLite
- **Trạng thái**: Accepted (2026-11-09), thay thế giả định "SQLite trong `/tmp`" của ADR-05
- **Bối cảnh**: Sau ADR-06, đăng nhập đã đúng trên mọi instance, nhưng hội thoại vẫn "lúc hiện lúc mất / hiện thiếu" sau khi đăng xuất và đăng nhập lại: mỗi instance Vercel có SQLite riêng, nên danh sách hội thoại và tin nhắn phụ thuộc request rơi vào instance nào (đo được trên production: 12 request `/api/conversations` song song trả lúc 1 lúc 0 hội thoại). Phê duyệt, đơn nghỉ, tài liệu tải lên và log có cùng vấn đề.
- **Quyết định**:
  - Một engine SQLAlchemy duy nhất (`DATABASE_URL`) cho dữ liệu nền tảng **và** bảng HRIS mẫu; PostgreSQL (Neon qua Vercel Marketplace) cho production, SQLite cho dev/test.
  - Toàn bộ SQL viết lại dialect-neutral: SQLAlchemy Core cho ghi (`insert ... returning`, `update` với biểu thức cột), `text()` với tham số đặt tên cho đọc, danh sách `IN` dùng expanding bind (danh sách rỗng hợp lệ); bỏ `sqlite3`, `?`, `lastrowid`, `substr`.
  - Seed bulk insert trong một transaction và bọc trong `pg_advisory_lock`, nên nhiều instance cold start đồng thời chỉ seed một lần.
  - Bộ nhớ đệm trong process tự làm mới: index RAG theo fingerprint `COUNT/MAX(id)` của `chunks`; sơ đồ tổ chức theo `ORG_CACHE_TTL`.
  - Phê duyệt "giữ chỗ" bằng `UPDATE ... WHERE status = 'pending'` (compare-and-set) thay cho đọc rồi ghi.
  - Engine PostgreSQL: `pool_pre_ping`, pool nhỏ, `prepare_threshold=None` (tương thích pooler transaction-mode).
- **Hệ quả**: Hội thoại, phê duyệt, KB và log nhất quán trên mọi instance và bền vững qua cold start. Đã kiểm chứng: 50/50 test trên cả SQLite và PostgreSQL 16; hai server khởi động đồng thời trên một database trống chỉ seed một lần; hội thoại tạo ở instance A được tiếp tục (giữ ngữ cảnh) ở instance B; 6 lệnh duyệt song song trên 2 instance cho đúng 1 lần thực thi. Đánh đổi: phụ thuộc dịch vụ database ngoài; schema đang tạo bằng `create_all` (chưa có migration, cần Alembic khi đổi cột trên dữ liệu thật).

## ADR-08: Production Hardening for Horizontal Scale (migrations, non-blocking I/O, SQL aggregation, ops)
- **Trạng thái**: Accepted (2026-11-09)
- **Bối cảnh**: Sau ADR-07 dữ liệu đã dùng chung, nhưng còn các điểm cản trở chạy nhiều instance / nhiều worker và vận hành lâu dài: (1) schema tạo bằng `create_all`, không nâng cấp được bảng đang có dữ liệu; (2) runtime `async` gọi DB đồng bộ ngay trên event loop (log LLM/tool, tạo phê duyệt, lưu hội thoại), một stream chậm làm đứng mọi stream khác trong process; (3) `/api/metrics` nạp toàn bộ `llm_calls` vào Python, "chờ tôi duyệt" lọc JSON trong Python, thiếu index trên khóa ngoại; (4) không có request id, log khó truy vết, lỗi 500 lộ chi tiết nội bộ; (5) không giới hạn đăng nhập sai; dọn dữ liệu chỉ chạy khi khởi động process.
- **Quyết định**:
  - **Alembic**: `0001` = baseline đúng bằng schema đang chạy, `0002` = index + bảng mới + backfill. `app.core.migrations.migrate()` chạy lúc khởi động trong `pg_advisory_lock`; DB tạo trước khi có migration được nhận diện và stamp `0001`. Test chặn lệch model/migration.
  - **Không chặn event loop**: mọi thao tác DB trong runtime và `chat_turn` chạy qua `asyncio.to_thread`; endpoint không cần async (`decide`) chuyển sang `def` để FastAPI chạy trong threadpool.
  - **Truy vấn mở rộng được**: KPI tính bằng `GROUP BY` / `COUNT DISTINCT` trong DB; bảng `pending_action_approvers` có index cho "chờ tôi duyệt"; index `conversations(user_id, updated_at)`, `chat_messages(conversation_id)`, `llm_calls(department, created_at)`, `pending_actions(requested_by)`, `pending_actions(status)`.
  - **Observability**: ASGI middleware gắn `X-Request-ID` (nhận từ client/`x-vercel-id` hoặc sinh mới) vào response và mọi dòng log; access log có thời gian xử lý; `LOG_FORMAT=json` cho log pipeline; `/api/health` kiểm tra DB.
  - **Bảo mật HTTP**: CSP, `X-Frame-Options: DENY`, `nosniff`, Referrer/Permissions-Policy, HSTS trên HTTPS; SRI cho script CDN; handler 500 chỉ trả thông điệp chung + `request_id`; giới hạn đăng nhập sai theo tài khoản, đếm trong DB nên đúng trên mọi instance.
  - **Vận hành**: `/api/internal/maintenance` (Vercel Cron hằng ngày, bảo vệ bằng `CRON_SECRET`) chạy purge hội thoại nhạy cảm và dọn bản ghi đăng nhập sai; cấu hình sai thì dừng khởi động (`Settings.validate()`), thiếu cấu hình quan trọng thì cảnh báo.
  - **Chuẩn hóa dự án**: `pyproject.toml` là nguồn dependency chính (PEP 621, Vercel/uv cài từ đây) + cấu hình ruff/pytest; `requirements*.txt` là bản sao pin chính xác cho pip/Docker, có test giữ khớp; CI GitHub Actions (ruff + pytest trên SQLite/PostgreSQL × Python 3.12/3.13), `Dockerfile` (non-root, healthcheck) + `docker-compose.yml`.
- **Hệ quả**: Có thể tăng số worker/instance mà không đổi code; nâng cấp schema an toàn trên dữ liệu thật; lỗi production truy vết được bằng mã lỗi người dùng nhìn thấy. 60/60 test trên SQLite và PostgreSQL. Đánh đổi: thêm phụ thuộc Alembic; khởi động lần đầu chạy migration (vài trăm ms); `Dockerfile` chưa được build thử trên máy phát triển (không có Docker daemon), cần CI build image trước khi dùng.

## ADR-09: Package-by-Domain Layout with Enforced Dependency Direction
- **Trạng thái**: Accepted (2026-11-09)
- **Bối cảnh**: `app/` có 18 module phẳng trộn hạ tầng, nghiệp vụ và adapter; `hris.py` (480 dòng) gộp schema, truy vấn, quy tắc lương, dữ liệu mẫu, sơ đồ tổ chức; `db.py` gộp engine với toàn bộ model ORM. Khó biết sửa ở đâu, dễ tạo phụ thuộc vòng.
- **Quyết định**:
  - Gom theo domain: `core/` (settings, db, migrations, observability), `access/` (principal, policy, auth), `hris/` (schema, queries, org, payroll, demo_data), `llm/` (client, pricing, base, gemini, openai_compat), `agents/` (registry, runtime, conversation), `models.py`, `bootstrap.py`; giữ `api/`, `rag/`, `tools/`.
  - Chiều phụ thuộc một chiều: `core ← models · access · hris · llm · rag ← tools · agents ← api ← bootstrap · main`, cưỡng chế bởi `tests/test_architecture.py` (phân tích AST, gồm cả import trong hàm) và cấm import tương đối.
  - `hris`, `access`, `llm` có API công khai trong `__init__.py`; `agents` import thẳng module con (tránh vòng `tools` ↔ `agents`).
  - Không để module "cầu nối" ở đường dẫn cũ: mọi import đã được chuyển; tên bảng và schema giữ nguyên nên **không cần migration**.
- **Hệ quả**: Thay HRIS mẫu bằng connector thật chỉ chạm `hris/demo_data.py`; thêm provider LLM chỉ chạm `llm/`; vi phạm kiến trúc làm CI đỏ. Code import theo đường dẫn cũ (`app.policy`, `app.db`, `app.hris` dạng module...) phải đổi (trong repo đã đổi hết). Kiểm chứng: 114/114 test trên SQLite và PostgreSQL; `alembic check` không thấy thay đổi schema.
