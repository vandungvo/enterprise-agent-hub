# Software Requirements Specification (SRS)

## 1. Functional Requirements (FR)

### FR-01: Multi-Agent Conversational Routing
- **Mô tả**: Hệ thống cung cấp một điểm tiếp nhận hội thoại duy nhất ("Trợ lý Sao Mai"). Router Agent phân tích ngữ cảnh câu hỏi của người dùng và ủy quyền (delegate) câu hỏi đến đúng agent chuyên môn (`people`, `insights`, `finance`, `it_helpdesk`, `company_info`).
- **Tiêu chí chấp nhận (Acceptance Criteria)**:
  - Router chỉ thấy và delegate được tới các agent mà người dùng có quyền truy cập theo cấu hình `platform.yaml`.
  - Hỗ trợ câu hỏi đa lĩnh vực bằng cách gọi nhiều agent lần lượt và tổng hợp câu trả lời.
  - Phản hồi được truyền trực tiếp về client qua Server-Sent Events (SSE) kèm trace các bước gọi tool.

### FR-02: Deterministic ABAC Data-Tier Security
- **Mô tả**: Kiểm soát quyền truy cập dữ liệu ở tầng mã nguồn xác định trước mọi truy vấn cơ sở dữ liệu.
- **Tiêu chí chấp nhận**:
  - Dựng lại đối tượng `Principal` (ID, đơn vị, chuỗi quản lý, cấp bậc L1-L8, vai trò tự động và vai trò gán) tại mỗi request.
  - Hỗ trợ các phạm vi truy cập: `self`, `direct_reports`, `subtree`, `same_unit`, `role_scope`, `group`.
  - Mọi trường hợp bị từ chối truy cập phải trả về thông báo lịch sự, không được đoán mò dữ liệu.

### FR-03: Personal Profile & Compensation Self-Service (C3)
- **Mô tả**: Cho phép nhân viên tự phục vụ tra cứu hồ sơ cá nhân, phiếu lương chi tiết và lịch sử điều chỉnh lương.
- **Tiêu chí chấp nhận**:
  - Nhân viên chỉ xem được lương của chính mình.
  - Quản lý hỏi lương của nhân viên cấp dưới trực tiếp chỉ được xem nếu là cấp dưới trực tiếp (với CEO/Ban điều hành) hoặc bị từ chối (với quản lý thông thường).
  - Kết quả tra cứu lương bị che mờ trong operational log và được ghi vào bảng kiểm toán `data_access_log`.

### FR-04: Leave Management & Team Absence Calendar
- **Mô tả**: Tra cứu số dư phép năm, lịch sử đơn nghỉ, xem lịch vắng mặt của đồng nghiệp trong cùng nhóm và nộp đơn nghỉ phép.
- **Tiêu chí chấp nhận**:
  - Đồng nghiệp trong cùng team chỉ thấy ngày vắng mặt, không thấy loại nghỉ (bảo vệ thông tin sức khỏe/nghỉ ốm).
  - Quản lý trực tiếp nhìn thấy đầy đủ loại nghỉ của cấp dưới.
  - Nộp đơn nghỉ tạo yêu cầu phê duyệt chuyển đến quản lý trực tiếp (`manager_id`).

### FR-05: Leadership & Aggregate Analytics (K-Anonymity)
- **Mô tả**: Cho phép quản lý và lãnh đạo tra cứu báo cáo headcount, tuyển mới, nghỉ việc, quỹ lương và ngân sách trong phạm vi đơn vị được quản lý.
- **Tiêu chí chấp nhận**:
  - Áp dụng k-anonymity: Ẩn các nhóm có số lượng nhân sự < 5 (với quản lý, HRBP) hoặc < 3 (với CFO, CEO).
  - Áp dụng Complementary Suppression: Nếu chỉ có duy nhất 1 nhóm bị ẩn, ẩn thêm nhóm nhỏ thứ hai để chống suy ngược bằng phép trừ tổng.

### FR-06: Financial Claims & Budget Management
- **Mô tả**: Tra cứu quy định công tác phí, hoàn ứng và nộp đề nghị thanh toán chi phí.
- **Tiêu chí chấp nhận**:
  - Đề nghị thanh toán có số tiền <= 20 triệu VNĐ chuyển đến Quản lý trực tiếp duyệt.
  - Đề nghị thanh toán có số tiền > 20 triệu VNĐ tự động chuyển tiếp lên Trưởng khối (Unit Head) duyệt.

### FR-07: IT Helpdesk & Support Tickets
- **Mô tả**: Hướng dẫn tự xử lý sự cố công nghệ và tạo ticket hỗ trợ IT.
- **Tiêu chí chấp nhận**:
  - Tra cứu hướng dẫn xử lý tài khoản, VPN, email trong KB IT Helpdesk.
  - Cho phép tạo ticket hỗ trợ IT và chuyển thẳng vào hệ thống mà không cần phê duyệt (`approval_override: { create_ticket: false }`).

### FR-08: Vietnamese Hybrid RAG with Document ACL
- **Mô tả**: Tìm kiếm tri thức văn bản lai giữa BM25 và Vector Embeddings với bộ lọc bảo mật theo từng tài liệu.
- **Tiêu chí chấp nhận**:
  - Hỗ trợ các định dạng file: `.pdf`, `.docx`, `.md`, `.txt`, `.csv`.
  - Phân quyền tài liệu theo `roles`, `units`, `min_level`. Tài liệu không được phép xem sẽ bị ẩn hoàn toàn, không lộ cả tiêu đề trong kết quả tìm kiếm.
  - Kết quả trả về trích dẫn rõ nguồn `[n]`.

### FR-09: Human-in-the-Loop Approval Queue
- **Mô tả**: Quản lý hàng đợi phê duyệt cho các hành động thay đổi trạng thái trong hệ thống.
- **Tiêu chí chấp nhận**:
  - Hiển thị danh sách yêu cầu chờ duyệt và yêu cầu đã gửi.
  - Người duyệt được kiểm tra tính hợp lệ: đúng người có thẩm quyền, trạng thái đang là PENDING, ngăn chặn tự duyệt và duyệt trùng lặp.

### FR-10: Governance, Audit & Usage Telemetry
- **Mô tả**: Bảng điều khiển quản trị, kiểm toán truy cập dữ liệu và đo lường sử dụng AI.
- **Tiêu chí chấp nhận**:
  - Cung cấp trang "Quyền của tôi" cho phép nhân viên xem ai đã xem dữ liệu nhạy cảm của mình.
  - Cung cấp trang "Kiểm toán dữ liệu" cho vai trò `auditor` và `chro`.
  - Cung cấp biểu đồ mức độ sử dụng AI, chi phí token, tỷ lệ cache hit, và độ trễ.

---

## 2. Non-Functional Requirements (NFR)

### NFR-01: Zero Prompt Injection Leakage
- Toàn bộ dữ liệu mật C3 và phạm vi truy cập dữ liệu phải được thẩm định tại tầng logic code (`app/policy.py`). Không có bất kỳ lệnh prompt injection hay jailbreak nào có thể mở rộng quyền của người dùng.

### NFR-02: Latency & Streaming Responsiveness
- Thời gian bắt đầu nhận token đầu tiên (Time to First Token - TTFT) qua SSE stream phải đạt dưới 1.5 giây.
- Thời gian hoàn tất phản hồi trung bình cho các câu hỏi thông thường phải dưới 3.0 giây.
- Thời gian đánh giá policy tại mỗi lượt gọi tool phải dưới 50ms.

### NFR-03: Provider Resilience & High Availability
- Adapter kết nối LLM phải có khả năng tự động xử lý mã lỗi 429 (Rate Limit) với cơ chế Exponential Backoff theo header `Retry-After`.
- Hỗ trợ chuyển đổi nhanh (Hot-switch) giữa Claude, Gemini và OpenAI-compatible/Ollama thông qua cấu hình biến môi trường.

### NFR-04: Data Privacy & Compliance
- Tuân thủ quy định bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP).
- Các phiên hội thoại chạm đến dữ liệu C3 phải tự động gắn nhãn bảo mật và được tự động thanh trừng sau 30 ngày (`SENSITIVE_RETENTION_DAYS`).
- Ký kết cam kết Zero Data Retention với các bên cung cấp dịch vụ LLM API.

### NFR-05: Maintainability & Dynamic Configuration
- Cho phép chỉnh sửa danh mục agent, prompt hệ thống và ma trận chính sách trong các file YAML và nạp lại cấu hình tức thì qua API `/api/admin/reload-config` mà không cần khởi động lại dịch vụ.
