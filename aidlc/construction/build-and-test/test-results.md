# Automated Test Execution Results

- **Executed At**: 2026-11-09T01:15:00+07:00
- **Test Command**: `.venv\Scripts\python -m pytest -q`
- **Result Summary**: **114 PASSED, 0 FAILED** trên SQLite **và** trên PostgreSQL 16 (`TEST_DATABASE_URL`); `ruff check .` sạch
- **Duration**: 13.1s (SQLite) / 15.8s (PostgreSQL)

## Test Breakdown by Module

| Test Module | Test Count | Pass Rate | Key Areas Validated |
|---|---|---|---|
| `tests/test_policy.py` | 23 | 100% | Phân quyền ABAC, self-access lương, từ chối xem lương người khác, k-anonymity, complementary suppression, ACL tài liệu, log kiểm toán |
| `tests/test_api.py` | 10 | 100% | FastAPI REST endpoints, đăng nhập và token ký HMAC (chống giả mạo/sửa chữ ký), endpoint theo vai trò, hàng đợi phê duyệt, kiểm toán |
| `tests/test_runtime.py` | 5 | 100% | Agent orchestration runtime, Router delegation, tool execution loop, context isolation |
| `tests/test_platform.py` | 4 | 100% | Nạp `platform.yaml`, đăng ký agents và knowledge bases, quyền dùng agent |
| `tests/test_gemini.py` | 4 | 100% | Adapter Gemini: function declaration schema, streaming mapping |
| `tests/test_architecture.py` | 51 | 100% | Chiều phụ thuộc giữa các package cho từng module (ADR-09), cấm import tương đối |
| `tests/test_hardening.py` | 8 | 100% | Request id, security headers, login throttling (429), cron auth, lỗi 500 không lộ chi tiết, validate cấu hình |
| `tests/test_migrations.py` | 2 | 100% | Model khớp migration (không drift); nhận DB tạo trước khi có migration, stamp + upgrade + backfill approver |
| `tests/test_openai_compat.py` | 4 | 100% | Adapter OpenAI-compatible (Groq, Ollama): message translation, tool call normalization |

## Lịch sử

| Thời điểm | Kết quả | Ghi chú |
|---|---|---|
| 2026-11-08T23:35:10Z | 47 passed (13.39s) | Baseline khi chạy Construction phase |
| 2026-11-09T00:30:55+07:00 | 48 passed (10.42s) | Thêm `test_session_token_is_signed_and_stateless` (ADR-06) |
| 2026-11-09T00:55:00+07:00 | 50 passed (SQLite 10.6s, PostgreSQL 11.6s) | ADR-07: thêm `test_health_reports_database`, `test_knowledge_index_picks_up_writes_from_other_instances` |
| 2026-11-09T01:15:00+07:00 | 60 passed (SQLite 13.1s, PostgreSQL 15.8s) | ADR-08: thêm `test_hardening.py`, `test_migrations.py` |
| 2026-11-09T01:25:00+07:00 | 63 passed (SQLite 12.5s) | Thêm `test_dependencies.py` sau sự cố deploy (xem rollback-runbook §3) |
| 2026-11-09T01:45:00+07:00 | 114 passed (SQLite 13.7s, PostgreSQL 16.6s) | ADR-09: tái cấu trúc package + `test_architecture.py` |

## Smoke test trên production (Vercel)

Đã kiểm tra trên https://ent-agents.vercel.app: UI và static trả 200; đăng nhập persona; 50 request song song có token (`/api/me`, `/api/conversations`, `/api/approvals`, `/api/metrics`, `/api/my-data-access`) đều 200 sau ADR-06 (trước đó lỗi 401 ngẫu nhiên); tìm kiếm KB trả kết quả; một lượt chat thật qua Groq ("Tôi còn bao nhiêu ngày phép?") chạy router → people → tool và trả lời đúng.

## Kiểm thử đa instance (local, PostgreSQL 16)

Hai server `uvicorn` riêng biệt (port 8101, 8102) cùng trỏ vào một database trống, khởi động đồng thời:

| Kịch bản | Kết quả |
|---|---|
| Cold start đồng thời | Seed đúng một lần (11 users, 108 employees, 9 documents, 45 chunks; không trùng) |
| Tạo hội thoại ở A, hỏi tiếp ở B với cùng `conversation_id` | B trả lời đúng ngữ cảnh; sau khi đăng nhập lại, cả A và B đều thấy 1 hội thoại, 4 tin nhắn |
| 6 lệnh duyệt song song (3 ở A, 3 ở B) cho cùng một yêu cầu | Đúng 1 `200` + 5 `409`; 1 đơn nghỉ được ghi; trạng thái `executed` |

## Xác nhận trên production sau ADR-07 (Neon PostgreSQL)

`GET /api/health` → `{"status":"ok","database":"postgresql"}`. Tài khoản `ceo` tạo hội thoại, hỏi tiếp lượt 2 (giữ ngữ cảnh), đăng nhập lại rồi gửi 15 request `/api/conversations` + 15 request `/api/conversations/{id}` song song: **15/15 trả 1 hội thoại, 15/15 trả đủ 4 tin nhắn** (trước ADR-07: lúc 1 lúc 0).

## Kiểm thử đa instance sau ADR-08 (local, PostgreSQL 16 trống)

Hai server khởi động đồng thời: schema được migrate một lần lên `0002`, seed một lần (11 users, 108 employees, 9 documents, 45 chunks); response có `X-Request-ID`, CSP, `X-Frame-Options`; access log JSON mang `request_id` và `duration_ms`; không có lỗi trong log của cả hai.

## Xác nhận trên production sau ADR-08

Bản preview kiểm tra `/api/health` trước, rồi promote. Trên https://ent-agents.vercel.app: health `ok` (postgresql); response có CSP, `X-Frame-Options`, `nosniff`, `X-Request-Id`; dữ liệu cũ còn nguyên sau migration (hội thoại của `ceo`); `/api/metrics` tính bằng SQL trả đúng; `/api/internal/maintenance` trả 404 khi chưa đặt `CRON_SECRET`; `dev.alpha` xin nghỉ qua chat → yêu cầu #1 xuất hiện trong hàng đợi "chờ tôi duyệt" của `manager.alpha` (bảng approver mới), sau đó đã từ chối để dọn dữ liệu thử.
