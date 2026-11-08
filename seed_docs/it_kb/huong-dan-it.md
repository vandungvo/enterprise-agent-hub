---
title: Hướng dẫn IT cho nhân viên
classification: internal
---
# Hướng dẫn IT cho nhân viên

## Kết nối VPN
1. Cài ứng dụng VPN từ Company Portal.
2. Đăng nhập bằng tài khoản công ty (SSO) và xác thực MFA.
3. Lỗi "Authentication failed": kiểm tra mật khẩu vừa đổi, khởi động lại máy rồi thử lại.
4. Kết nối được nhưng không vào hệ thống nội bộ: ngắt VPN, chạy `ipconfig /flushdns`, kết nối lại.
5. Không nhận mã MFA khi đổi điện thoại: tạo ticket loại "account" để IT đăng ký lại.

## Mật khẩu và tài khoản
- Mật khẩu tối thiểu 14 ký tự, đổi 90 ngày/lần. Tự đặt lại mật khẩu qua cổng SSPR khi đã đăng ký MFA.
- Tài khoản bị khóa sau 5 lần sai: tự mở sau 30 phút hoặc tạo ticket.
- IT không bao giờ hỏi mật khẩu hay mã OTP của bạn.

## Cấp quyền truy cập hệ thống
- Yêu cầu quyền (repo mã nguồn, cloud console, công cụ nội bộ) qua ticket loại "access_request", ghi rõ hệ thống và lý do. Quyền được quản lý trực tiếp và chủ sở hữu hệ thống phê duyệt.
- Quyền vào hệ thống production và dữ liệu khách hàng chỉ cấp theo nguyên tắc "cần biết" và có thời hạn.

## Email và lừa đảo
- Email nghi ngờ lừa đảo: không bấm link, không mở tệp; dùng nút "Report Phishing".
- Sự cố bảo mật (lộ mật khẩu, mất thiết bị, mã độc): gọi hotline 1900 và tạo ticket "security" mức critical.

## SLA ticket
- critical: phản hồi 15 phút, xử lý 4 giờ. high: phản hồi 1 giờ, xử lý 1 ngày làm việc.
- medium: xử lý 2 ngày làm việc. low: xử lý 5 ngày làm việc.
