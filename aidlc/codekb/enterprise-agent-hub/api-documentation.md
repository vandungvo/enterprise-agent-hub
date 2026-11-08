# API Documentation

> Đồng bộ với `app/api/*.py` (2026-11-09). Mọi endpoint có cột Auth = Yes yêu cầu header `Authorization: Bearer <token>`.

## 0. Health

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/health` | `{status, database: sqlite \| postgresql, database_ok}`; 503 nếu không kết nối được database | No |

## 1. Authentication & Identity

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/demo-users` | Danh sách tài khoản demo theo persona và mật khẩu demo | No |
| `POST` | `/api/login` | Body `{email, password}`. Sai quá `LOGIN_MAX_FAILURES` lần trong `LOGIN_WINDOW_MINUTES` phút → `429` + `Retry-After`. Trả về `{token}`: token **stateless ký HMAC-SHA256** (email + hạn dùng `SESSION_HOURS`), không lưu ở server. Không có endpoint logout: client xóa token, token tự hết hạn | No |
| `GET` | `/api/me` | Principal hiện tại (đơn vị, cấp bậc, vai trò, phạm vi quyền từng resource), danh sách agent và KB được dùng | Yes |

Principal **không** nằm trong token: mỗi request, server xác thực chữ ký rồi dựng lại Principal từ HRIS theo email, nên thay đổi vai trò hoặc nghỉ việc có hiệu lực ngay.

## 2. Chat & AI Streaming

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Body `{message, conversation_id?, agent_id?}`. Trả về SSE stream (`data: {...}`) với các sự kiện `conversation`, `agent_start`, `text`, `tool_call`, `tool_result`, `agent_end`, `done`, `error` |
| `GET` | `/api/conversations` | 100 cuộc hội thoại gần nhất của người dùng |
| `GET` | `/api/conversations/{id}` | Chi tiết hội thoại kèm tin nhắn, nguồn trích dẫn, trace |
| `DELETE` | `/api/conversations/{id}` | Xóa hội thoại của chính mình |
| `POST` | `/api/messages/{id}/feedback` | Body `{value: 1 \| -1, comment?}`: đánh giá 👍/👎 |

## 3. Knowledge Base & Documents

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/kbs/{kb_id}/documents` | Tài liệu trong KB; tài liệu không đọc được bị ẩn cả tiêu đề (trừ người quản lý KB) |
| `POST` | `/api/kbs/{kb_id}/documents` | Multipart: `file`, `title?`, `classification`, `roles?`, `min_level?`. Chỉ vai trò `managed_by` của KB; tối đa 20MB (.md, .txt, .pdf, .docx, .csv) |
| `DELETE` | `/api/documents/{id}` | Xóa tài liệu (người quản lý KB) |
| `POST` | `/api/kbs/search` | Body `{query, kb_ids?, top_k}`: tìm kiếm hybrid có lọc ACL tài liệu |

## 4. Human-in-the-Loop Approvals

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/approvals?scope=mine` | Yêu cầu do chính người dùng gửi |
| `GET` | `/api/approvals?scope=review` | Yêu cầu đang chờ người dùng duyệt (theo tuyến báo cáo) |
| `POST` | `/api/approvals/{id}/decision` | Body `{approve: bool, note?}`. Chỉ người trong danh sách duyệt; yêu cầu được giữ chỗ (`processing`) trước khi chạy để không thực thi hai lần |

## 5. Data-Access Transparency & Audit

| Method | Endpoint | Description | Vai trò |
|---|---|---|---|
| `GET` | `/api/my-data-access` | Ai đã xem dữ liệu nhạy cảm của tôi | Mọi người |
| `GET` | `/api/audit/data-access?denied_only=` | Nhật ký mọi truy cập nhạy cảm và mọi lần bị từ chối | `auditor` |

## 6. Usage KPIs & Platform Admin

| Method | Endpoint | Description | Vai trò |
|---|---|---|---|
| `GET` | `/api/metrics?days=30` | Lượt gọi LLM, chi phí, cache hit, độ trễ, adoption, feedback, từ chối; theo khối, agent, ngày, tool | `platform_admin`, `exec`, `chro` |
| `GET` | `/api/admin/agents` | Cấu hình agent (model, tool, KB, quyền dùng, cờ phê duyệt, system prompt) | `platform_admin`, `auditor` |
| `GET` | `/api/admin/policies` | Toàn bộ policy resource | `platform_admin`, `auditor`, `chro` |
| `POST` | `/api/admin/reload` | Nạp lại `platform.yaml` và `policies.yaml` không cần restart | `platform_admin` |
| `GET` | `/api/admin/audit?limit=100` | Nhật ký tool call (output nhạy cảm đã bị ẩn) | `platform_admin`, `auditor` |

## 7. Static UI

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | `static/index.html` |
| `GET` | `/static/*` | `app.js`, `styles.css` |

## 8. Internal (scheduler)

| Method | Endpoint | Description | Auth |
|---|---|---|---|
| `GET` | `/api/internal/maintenance` | Purge hội thoại nhạy cảm quá hạn, dọn bản ghi đăng nhập sai > 1 ngày. Vercel Cron gọi hằng ngày | `Authorization: Bearer <CRON_SECRET>`; không đặt `CRON_SECRET` → 404 |

## Quy ước chung

- Mọi response có header `X-Request-ID` (gửi kèm `X-Request-ID` để tự đặt id). Lỗi 500 trả `{"detail": "...", "request_id": "..."}`; lỗi trong stream chat trả sự kiện `error` kèm mã lỗi đó.
- Security headers: `Content-Security-Policy`, `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Referrer-Policy`, `Permissions-Policy`, HSTS khi qua HTTPS.
