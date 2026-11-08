# Operational Runbooks

## Runbook 1: Xử lý sự cố LLM Provider trả lỗi 429 hoặc Down
1. **Dấu hiệu**: Hệ thống trả về thông báo lỗi kết nối hoặc độ trễ phản hồi tăng đột biến.
2. **Kiểm tra**:
   - Mở dashboard `/usage`, kiểm tra tỷ lệ lỗi theo provider.
   - Kiểm tra log container: `docker logs -f enterprise-agent-hub | grep 429`.
3. **Xử lý nhanh**:
   - Nếu Anthropic gặp sự cố diện rộng: Đổi biến môi trường sang Gemini hoặc OpenAI trong `.env`:
     ```env
     LLM_PROVIDER=gemini
     # hoặc
     LLM_PROVIDER=openai_compat
     ```
   - Khởi động lại container hoặc reload:
     ```bash
     docker compose restart app
     ```

## Runbook 2: Xử lý sự cố nghi ngờ rò rỉ dữ liệu hoặc Bypass Policy
1. **Dấu hiệu**: Cảnh báo từ ALM-01 hoặc khiếu nại từ người dùng.
2. **Hành động tức thì**:
   - Kích hoạt quy trình cách ly: Tạm dừng dịch vụ chat hoặc ngắt quyền gọi công cụ của `people` và `insights` agent trong `platform.yaml`.
   - Nạp lại cấu hình ngay lập tức: `POST /api/admin/reload-config`.
3. **Điều tra nguyên nhân**:
   - Truy vấn bảng `data_access_log`:
     ```sql
     SELECT * FROM data_access_log WHERE decision = 'GRANTED' AND resource = 'compensation.individual' ORDER BY timestamp DESC LIMIT 50;
     ```
   - So sánh `actor_id` với `target_id` và quan hệ báo cáo `manager_id` để xác định truy cập có hợp lệ hay không.
4. **Báo cáo**: Gửi báo cáo phân tích nguyên nhân gốc rễ (RCA) cho CHRO, DPO và Hội đồng bảo mật trong vòng 24 giờ.
