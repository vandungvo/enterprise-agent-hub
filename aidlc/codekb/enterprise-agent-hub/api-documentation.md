# API Documentation

## 1. Authentication & Session Endpoints

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `POST` | `/api/login` | Đăng nhập demo bằng employee ID hoặc email, trả về session cookie | No |
| `POST` | `/api/logout` | Đăng xuất và vô hiệu hóa phiên | Yes |
| `GET` | `/api/me` | Lấy thông tin Principal hiện tại (đơn vị, cấp bậc, vai trò, quyền) | Yes |
| `GET` | `/api/demo-users` | Danh sách tài khoản mẫu theo từng persona để test | No |

## 2. Chat & AI Streaming Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat` | Khởi tạo lượt hội thoại mới, trả về Server-Sent Events (SSE) stream các sự kiện: `agent_start`, `tool_call`, `tool_result`, `text_delta`, `done`, `error`. |
| `GET` | `/api/conversations` | Danh sách lịch sử các cuộc hội thoại của người dùng |
| `GET` | `/api/conversations/{id}` | Chi tiết một cuộc hội thoại kèm lịch sử tin nhắn |
| `DELETE`| `/api/conversations/{id}` | Xóa một cuộc hội thoại |
| `POST` | `/api/messages/{id}/feedback`| Đánh giá 👍 hoặc 👎 kèm lý do |

## 3. Human-in-the-Loop Approval Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/approvals/pending` | Danh sách các yêu cầu đang chờ người dùng hiện tại phê duyệt (theo tuyến báo cáo) |
| `GET` | `/api/approvals/my-requests` | Danh sách các yêu cầu do chính người dùng gửi lên |
| `POST` | `/api/approvals/{id}/approve` | Phê duyệt yêu cầu (kiểm tra quyền duyệt và trạng thái PENDING) |
| `POST` | `/api/approvals/{id}/reject` | Từ chối yêu cầu kèm lý do |

## 4. Permissions & Audit Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/my-permissions` | Xem phạm vi truy cập dữ liệu thực tế được cấp theo ABAC policy |
| `GET` | `/api/my-data-access` | Xem nhật ký các lượt ai đã tra cứu dữ liệu nhạy cảm C3 của mình |
| `GET` | `/api/audit/logs` | Xem toàn bộ nhật ký truy cập nhạy cảm (chỉ dành cho vai trò `auditor`, `chro`) |

## 5. Knowledge Base & Documents Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/knowledge-bases` | Danh sách các KB người dùng được phép truy cập |
| `GET` | `/api/knowledge-bases/{id}/documents` | Danh sách tài liệu trong KB (lọc theo ACL tài liệu) |
| `POST` | `/api/knowledge-bases/{id}/upload` | Tải lên tài liệu mới (.pdf, .docx, .md, .txt, .csv) (kiểm tra vai trò `managed_by`) |
| `DELETE`| `/api/documents/{id}` | Xóa tài liệu khỏi KB |

## 6. Admin & Telemetry Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/usage-metrics` | Thống kê số lượng token, chi phí, tỷ lệ cache hit, độ trễ theo đơn vị, agent, ngày |
| `POST` | `/api/admin/reload-config` | Nạp lại cấu hình `platform.yaml` và `policies.yaml` mà không cần restart server |
