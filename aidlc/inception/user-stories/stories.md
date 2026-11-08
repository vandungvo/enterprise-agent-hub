# User Stories & Acceptance Criteria

## Epic 1: Tự phục vụ Thông tin cá nhân & Đãi ngộ (Self-Service & Compensation)

### US-01: Tra cứu phiếu lương chi tiết
- **Là**: Nhân viên (`employee`)
- **Tôi muốn**: Hỏi trợ lý AI về phiếu lương tháng gần nhất của tôi và được giải thích chi tiết các khoản trừ
- **Để**: Tôi hiểu rõ thu nhập thực nhận, tiền đóng bảo hiểm và thuế TNCN mà không cần hỏi phòng Nhân sự.
- **Tiêu chí chấp nhận (Gherkin)**:
  - *Given* Tôi đã đăng nhập với tài khoản `dev.alpha`
  - *When* Tôi nhắn: "Cho tôi xem phiếu lương tháng 10 và giải thích các khoản trừ"
  - *Then* Hệ thống gọi tool `get_payslip(employee_id="dev.alpha", month=10)`
  - *And* Kết quả hiển thị chi tiết Gross, Bảo hiểm, Thuế TNCN, Net thực nhận
  - *And* Một bản ghi kiểm toán được ghi vào `data_access_log`
  - *Traceability*: FR-03, NFR-01

### US-02: Ngăn chặn người dùng xem lương người khác
- **Là**: Nhân viên hoặc Quản lý thông thường
- **Tôi muốn**: Thử hỏi lương của một đồng nghiệp khác
- **Để**: Kiểm tra tính an toàn của hệ thống
- **Tiêu chí chấp nhận**:
  - *Given* Tôi đăng nhập với tư cách `manager.alpha`
  - *When* Tôi nhắn: "Cho tôi xem lương của kỹ sư A trong team tôi"
  - *Then* Policy engine xác định resource `compensation.individual` chỉ cho phép `self` đối với quản lý
  - *And* Trợ lý từ chối lịch sự: "Bạn không có quyền truy cập thông tin lương cá nhân của nhân sự này."
  - *And* Ghi nhận một sự kiện `DENIED` vào `data_access_log`
  - *Traceability*: FR-02, FR-03, NFR-01

---

## Epic 2: Quản lý Nghỉ phép & Lịch vắng mặt (Leave Management)

### US-03: Xem số dư phép và nộp đơn nghỉ phép
- **Là**: Nhân viên (`employee`)
- **Tôi muốn**: Kiểm tra số ngày phép còn lại và nộp đơn xin nghỉ phép 2 ngày
- **Để**: Tôi có thể sắp xếp kỳ nghỉ mà không phải điền biểu mẫu giấy
- **Tiêu chí chấp nhận**:
  - *Given* Tôi nhắn: "Tôi còn bao nhiêu ngày phép và muốn nghỉ ngày 12-13/11"
  - *When* Hệ thống kiểm tra số dư ngày phép qua `get_leave_balance` thấy còn đủ ngày
  - *Then* Hệ thống gọi `submit_leave_request` và tạo yêu cầu trong hàng đợi phê duyệt
  - *And* Phản hồi thông báo: "Đơn nghỉ phép đã được chuyển tới quản lý của bạn để phê duyệt."
  - *Traceability*: FR-04, FR-09

### US-04: Quản lý phê duyệt đơn nghỉ phép của cấp dưới
- **Là**: Quản lý trực tiếp (`manager`)
- **Tôi muốn**: Xem danh sách đơn nghỉ của team và bấm nút phê duyệt trực tiếp trên giao diện
- **Để**: Cấp dưới của tôi có thể hoàn tất thủ tục nghỉ phép kịp thời
- **Tiêu chí chấp nhận**:
  - *Given* `manager.alpha` mở trang "Phê duyệt"
  - *When* Nhìn thấy đơn nghỉ phép của `dev.alpha` với trạng thái PENDING
  - *Then* Bấm nút [Duyệt], hệ thống cập nhật trạng thái đơn thành APPROVED và trừ số dư ngày phép
  - *Traceability*: FR-04, FR-09

---

## Epic 3: Báo cáo & Phân tích Lãnh đạo (Leadership Analytics)

### US-05: Tra cứu biến động nhân sự và quỹ lương khối
- **Là**: Lãnh đạo Khối (`head.games`) hoặc CEO
- **Tôi muốn**: Hỏi về headcount hiện tại, tỷ lệ nghỉ việc và tổng quỹ lương 6 tháng gần nhất của Khối Games
- **Để**: Nắm bắt sức khỏe tổ chức và điều hành kế hoạch nhân sự
- **Tiêu chí chấp nhận**:
  - *Given* Đăng nhập với tài khoản `head.games`
  - *When* Hỏi: "Headcount hiện tại và quỹ lương của Khối Games?"
  - *Then* Router ủy quyền tới `insights` agent
  - *And* `workforce_analytics` trả về số liệu tổng hợp trong phạm vi khối Games
  - *And* Các nhóm phòng ban dưới 5 người tự động bị ẩn (k-anonymity) kèm thông báo bảo vệ dữ liệu cá nhân
  - *Traceability*: FR-05, NFR-01

---

## Epic 4: Tra cứu Tri thức & Quy định (Enterprise Knowledge & RAG)

### US-06: Tra cứu chính sách công tác phí có trích dẫn nguồn
- **Là**: Nhân viên (`employee`)
- **Tôi muốn**: Hỏi định mức khách sạn khi đi công tác Hà Nội
- **Để**: Tuân thủ đúng quy định tài chính của tập đoàn
- **Tiêu chí chấp nhận**:
  - *Given* Nhân viên hỏi: "Quy định công tác phí tại Hà Nội là bao nhiêu?"
  - *When* Hệ thống tìm kiếm lai BM25 + Vector trong KB `finance_policy`
  - *Then* Trả về câu trả lời chính xác định mức và trích dẫn mã nguồn tài liệu `[1]`
  - *Traceability*: FR-08, NFR-02
