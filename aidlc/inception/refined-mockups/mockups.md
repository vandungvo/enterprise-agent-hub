# Refined Mockups & Interaction Specifications

## 1. Web Portal Interface Specification
Giao diện người dùng của Enterprise Agent Hub là Single Page Application xây dựng bằng HTML5/CSS/JavaScript thuần không cần build step, tích hợp 7 phân hệ chính:

### 1.1 Chat Panel Layout
- **Thanh tiêu đề**: Logo Sao Mai Group, Tên hệ thống, Bộ chuyển đổi persona demo (dev.alpha, manager.alpha, head.games, ceo, cnb, itadmin), Nút tạo phiên chat mới.
- **Vùng tin nhắn**:
  - Bong bóng tin nhắn người dùng (Right-aligned, nền xanh thương hiệu).
  - Bong bóng tin nhắn AI (Left-aligned, nền trắng/xám nhẹ, render Markdown, KaTeX, Code highlight).
  - Khối Trace Accordion (Collapsible): Hiển thị chi tiết từng bước agent delegate, tên công cụ, tham số và kết quả rút gọn.
  - Thanh tiện ích tin nhắn: Nút Copy, Đánh giá 👍 / 👎 kèm popup nhập phản hồi.
- **Khung nhập liệu**: Ô input co giãn tự động (auto-expanding textarea), nút bấm gửi (Send button), phím tắt `Enter` để gửi, `Shift+Enter` xuống dòng.

### 1.2 Approval Queue View
- **Tab chuyển đổi**: "Chờ tôi duyệt" (Badge đếm số đơn pending) và "Tôi đã gửi".
- **Bảng danh sách yêu cầu**: Cột Mã yêu cầu, Loại nghiệp vụ (Đơn nghỉ phép, Đề nghị thanh toán, Ticket IT), Người gửi, Đơn vị, Ngày tạo, Tóm tắt nội dung.
- **Hành động**: Nút [Phê duyệt] (Xanh lá) và [Từ chối] (Đỏ) có dialog xác nhận lý do từ chối.

### 1.3 My Permissions & Access Audit View
- **Thẻ thông tin danh tính**: Chức danh, Đơn vị, Tuyến quản lý, Cấp bậc (L1-L8), Danh sách vai trò gán.
- **Bảng ma trận quyền**: Liệt kê từng loại dữ liệu (Lương cá nhân, Quỹ lương team, Hồ sơ, Ngân sách) và phạm vi được phép truy cập thực tế.
- **Bảng kiểm toán cá nhân**: "Ai đã xem dữ liệu nhạy cảm của bạn?" - Hiển thị thời gian, người xem, chức vụ và loại dữ liệu C3 đã truy cập.

## 2. Accessibility Checklist (WCAG 2.1 AA)
- [x] Tỷ lệ tương phản màu văn bản (Contrast ratio) >= 4.5:1 đối với văn bản thông thường.
- [x] Đầy đủ cấu trúc phân cấp thẻ Heading (H1 cho phân hệ, H2 cho vùng nội dung, H3 cho thẻ con).
- [x] Hỗ trợ điều hướng hoàn toàn bằng bàn phím (Tab order tuần tự, Focus indicator rõ nét).
- [x] Các vùng động (SSE Streaming) có thuộc tính `aria-live="polite"` để Screen Reader đọc cập nhật mà không ngắt người dùng.
