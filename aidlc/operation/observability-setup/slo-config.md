# Service Level Objectives (SLO) Configuration

## Core SLOs

| SLO Target | Service Level Indicator (SLI) | Objective (Mục tiêu cam kết) | Đo lường |
|---|---|---|---|
| **Sự sẵn sàng (Availability)** | Tỷ lệ HTTP 2xx/3xx trên tổng request (không tính lỗi client) | **99.9%** hàng tháng | Gateway metrics |
| **Độ trễ phản hồi (Latency)** | Thời gian trả về token đầu tiên (TTFT) qua SSE stream | **p95 < 1.5s**, **p99 < 3.0s** | SSE start telemetry |
| **Độ chính xác bảo mật (Security)** | Tỷ lệ vi phạm rò rỉ dữ liệu ngoài chính sách ABAC | **0.00% (Không chấp nhận sai sót)** | `data_access_log` & Red-team tests |
| **Độ hài lòng người dùng (CSAT)**| Tỷ lệ phản hồi tích cực (Thumbs Up) trên tổng lượt đánh giá | **>= 90%** hài lòng | Bảng phản hồi người dùng |
| **Thời gian lưu trữ dữ liệu C3** | Tỷ lệ phiên hội thoại C3 được thanh trừng sau 30 ngày | **100%** đúng thời hạn | Scheduled retention cron |
