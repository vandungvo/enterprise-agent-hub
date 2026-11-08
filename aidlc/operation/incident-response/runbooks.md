# Operational Runbooks

## Runbook 0: Truy vết một lỗi người dùng báo
1. Người dùng thấy "Lỗi hệ thống … (mã lỗi: `<id>`)" hoặc response 500 có `request_id`.
2. Tìm id đó trong log: `vercel logs ent-agents.vercel.app | grep <id>` (log JSON: lọc trường `request_id`). Mọi dòng log của request đó, gồm traceback, mang cùng id.

## Runbook 1: Xử lý sự cố LLM Provider trả lỗi 429 hoặc Down
1. **Dấu hiệu**: Hệ thống trả về thông báo lỗi kết nối hoặc độ trễ phản hồi tăng đột biến.
2. **Kiểm tra**:
   - Mở trang *Mức độ sử dụng AI* (`GET /api/metrics`), kiểm tra độ trễ, số lỗi theo agent/tool.
   - Xem log runtime:
     ```bash
     vercel logs ent-agents.vercel.app          # Vercel (môi trường hiện tại)
     kubectl logs -f deploy/enterprise-agent-hub | grep 429   # mục tiêu production
     ```
3. **Xử lý nhanh**: đổi sang provider dự phòng.
   - Giá trị hợp lệ của `LLM_PROVIDER`: `anthropic` | `gemini` | `groq` | `ollama` | `lmstudio` | `openrouter` | `openai`.
   - Trên Vercel:
     ```bash
     vercel env rm LLM_PROVIDER production
     vercel env add LLM_PROVIDER production     # nhập ví dụ: gemini
     vercel --prod                              # biến mới chỉ có hiệu lực sau khi deploy lại
     ```
   - Trên máy chủ cố định: sửa `.env` rồi khởi động lại tiến trình (biến môi trường chỉ đọc lúc khởi động; `POST /api/admin/reload` chỉ nạp lại YAML).

## Runbook 2: Xử lý sự cố nghi ngờ rò rỉ dữ liệu hoặc Bypass Policy
1. **Dấu hiệu**: Cảnh báo từ ALM-01 hoặc khiếu nại từ người dùng.
2. **Hành động tức thì**:
   - Kích hoạt quy trình cách ly: Tạm dừng dịch vụ chat (`vercel project pause enterprise-agent-hub` trên Vercel) hoặc ngắt quyền gọi công cụ của `people` và `insights` agent trong `platform.yaml`.
   - Nạp lại cấu hình: `POST /api/admin/reload` (máy chủ cố định) hoặc deploy lại (Vercel).
   - Nếu nghi token bị lộ: đổi `AGENTHUB_SECRET` và deploy lại để vô hiệu hóa mọi phiên.
3. **Điều tra nguyên nhân**:
   - Truy vấn bảng `data_access_log` (hoặc `GET /api/audit/data-access` với vai trò `auditor`):
     ```sql
     SELECT created_at, actor_name, actor_employee_id, target_employee_id, scope, conversation_id
     FROM data_access_log
     WHERE allowed = 1 AND resource = 'compensation.individual'
     ORDER BY created_at DESC LIMIT 50;
     ```
   - So sánh `actor_employee_id` với `target_employee_id` và quan hệ báo cáo trong HRIS để xác định truy cập có hợp lệ hay không.
4. **Báo cáo**: Gửi báo cáo phân tích nguyên nhân gốc rễ (RCA) cho CHRO, DPO và Hội đồng bảo mật trong vòng 24 giờ.
