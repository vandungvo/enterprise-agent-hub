# Observability Setup & Monitoring Dashboards

## 1. Built-in Telemetry Dashboard (`/usage`)
Hệ thống cung cấp sẵn bảng điều khiển đo lường trực quan trong giao diện Web với các chỉ số:
- **Tần suất sử dụng theo đơn vị**: Số lượt hỏi theo khối (Games, Pay, Cloud) và theo phòng ban.
- **Phân bổ Agent**: Tỷ lệ câu hỏi được điều phối tới `people`, `insights`, `finance`, `it_helpdesk`, `company_info`.
- **Đo lường Token & Chi phí**:
  - Input tokens vs Output tokens.
  - Tỷ lệ cache hit nhờ Anthropic Prompt Caching (tiết kiệm chi phí).
  - Chi phí ước tính theo USD/VNĐ theo từng ngày.
- **Hiệu năng & Trải nghiệm**:
  - Độ trễ trung bình và độ trễ p95 theo từng agent.
  - Tỷ lệ đánh giá phản hồi của người dùng: Tỷ lệ 👍 / 👎 và lý do không hài lòng.

## 2. Security & Policy Audit Dashboard (`/audit`)
- Thống kê số lượt truy cập dữ liệu nhạy cảm C3 thành công vs số lượt bị từ chối (`DENIED`).
- Danh sách 10 tài khoản có tần suất truy vấn dữ liệu nhạy cảm cao nhất để phát hiện dấu hiệu bất thường.
- Bộ lọc theo thời gian, theo người dùng, theo tài nguyên (`compensation`, `profile`, `leave`).
