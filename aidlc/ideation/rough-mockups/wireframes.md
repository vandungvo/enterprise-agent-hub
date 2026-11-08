# Wireframes & Conceptual Layouts

## 1. Global Navigation & Layout Architecture
Giao diện ứng dụng sử dụng cấu trúc Responsive Layout chia làm 2 phần chính: Sidebar điều hướng bên trái và Khung nội dung chính bên phải [Q1].

```
+-----------------------------------------------------------------------------+
|  [Logo] Sao Mai Group | Enterprise Agent Hub           User: Nguyen Van A v |
+------------------+----------------------------------------------------------+
|  NAVIGATION      |  MAIN CONTENT VIEW                                       |
|  - 💬 Trợ lý AI  |                                                          |
|  - ✅ Phê duyệt  |  (Dynamic view based on selected navigation tab)         |
|  - 🔐 Quyền của  |                                                          |
|       tôi        |                                                          |
|  - 📚 Tri thức   |                                                          |
|  - 📊 Sử dụng AI |                                                          |
|  - 🛡️ Kiểm toán  |                                                          |
|  - ⚙️ Quản trị   |                                                          |
|                  |                                                          |
|                  |                                                          |
|  Switch Persona  |                                                          |
|  [dev.alpha    v]|                                                          |
+------------------+----------------------------------------------------------+
```

## 2. Screen 1: AI Chat Assistant (`/chat`)
Giao diện hội thoại tương tác thông minh với khả năng hiển thị trace thực thi của Agent [Q2].

```
+-----------------------------------------------------------------------------+
|  Trợ lý Sao Mai                                            [New Chat] [+]   |
+-----------------------------------------------------------------------------+
|  [User]: Xem phiếu lương tháng 10 của tôi và giải thích các khoản trừ       |
|                                                                             |
|  [Agent]: v Đang thực thi...                                                |
|    +-- [Router] Phân tích intent: "compensation query" -> delegate "people"  |
|    +-- [Agent People] Gọi tool: get_payslip(employee_id="EMP01", month=10)   |
|    +-- [Policy Check] Resource: compensation.individual -> PERMITTED (self) |
|    +-- [Result] Lương gross: 45,000,000; BH: 4,725,000; Thuế: 3,250,000      |
|                                                                             |
|  Phiếu lương tháng 10/2026 của bạn như sau:                                 |
|  - Lương Gross: 45.000.000 VNĐ                                              |
|  - Các khoản bảo hiểm bắt buộc: 4.725.000 VNĐ                               |
|  - Thuế TNCN tạm tính: 3.250.000 VNĐ                                        |
|  -> Thực nhận: 37.025.000 VNĐ.                                              |
|                                                                             |
|  [👍 Thích] [👎 Không hài lòng]                           Copy | Retry      |
+-----------------------------------------------------------------------------+
|  [ Nhập câu hỏi cho Trợ lý Sao Mai...                           ] [ Gửi > ] |
+-----------------------------------------------------------------------------+
```

## 3. Screen 2: Approval Queue (`/approvals`)
Hàng đợi phê duyệt cho người quản lý duyệt đơn nghỉ, công tác phí, ticket [Q1].

```
+-----------------------------------------------------------------------------+
|  Hàng đợi Phê duyệt                                                         |
|  [ Chờ tôi duyệt (2) ]   [ Tôi đã gửi (1) ]   [ Lịch sử đã duyệt ]          |
+-----------------------------------------------------------------------------+
|  Mã đơn  | Loại yêu cầu  | Người gửi     | Nội dung tóm tắt   | Thao tác    |
|----------+---------------+---------------+--------------------+-------------|
|  REQ-102 | Đơn nghỉ phép | Tran Thi B    | Nghỉ phép 2 ngày   | [Duyệt]     |
|          |               | (Studio Alpha)| (12/11 - 13/11)    | [Từ chối]   |
|----------+---------------+---------------+--------------------+-------------|
|  REQ-105 | Đề nghị TT    | Le Van C      | Mua thiết bị test  | [Duyệt]     |
|          |               | (Dev Team)    | 15.000.000 VNĐ     | [Từ chối]   |
+-----------------------------------------------------------------------------+
```

## 4. Screen 3: My Permissions (`/my-permissions`)
Minh bạch quyền hạn và danh tính: Xem phạm vi được cấp quyền và ai đã xem dữ liệu C3 của tôi [Q1].

```
+-----------------------------------------------------------------------------+
|  Quyền & Nhật ký Dữ liệu cá nhân                                            |
+-----------------------------------------------------------------------------+
|  Vai trò: Quản lý trực tiếp (manager.alpha) | Khối: Sao Mai Games           |
|  Phạm vi dữ liệu được phép xem:                                             |
|  - Thông tin cá nhân: Bản thân                                              |
|  - Thông tin công việc & nghỉ phép: Tuyến báo cáo trực tiếp (9 nhân sự)     |
|  - Số liệu tổng hợp lương: Tuyến báo cáo (Áp dụng k-anonymity k=5)          |
|                                                                             |
|  Nhật ký: Ai đã xem dữ liệu nhạy cảm của bạn?                               |
|  + 05/11/2026 14:20 | Hoang Van D (C&B Lead) đã tra cứu Phiếu lương tháng 10|
|  + 01/11/2026 09:15 | Tran Van E (HRBP Games) đã xem Hồ sơ nhân sự         |
+-----------------------------------------------------------------------------+
```

## Accessibility Notes
- Mỗi màn hình tuân thủ cấu trúc phân cấp thẻ rõ ràng: Heading h1 cho tiêu đề phân hệ, h2 cho các khối dữ liệu.
- Vùng điều hướng (Sidebar) sử dụng landmark `<nav>`, nội dung chính đặt trong `<main>`, thông báo trạng thái đặt trong `aria-live="polite"`.
- Hỗ trợ đầy đủ phím tắt bàn phím (Tab, Enter, Esc) cho việc mở/đóng modal và gửi tin nhắn chat.

## Assumptions & Open Questions
None. [Q1, Q2]
