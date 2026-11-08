# Rough Mockups Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.
- [scope-doc] `aidlc/ideation/scope-definition/scope-document.md`

## Q1. [Design] Giao diện người dùng bao gồm những màn hình/phân hệ chính nào?
A. Web Portal tích hợp 7 phân hệ qua thanh điều hướng bên (Sidebar Navigation): 1. Trợ lý AI (Chat); 2. Phê duyệt (Approvals); 3. Quyền của tôi (My Permissions & Access audit); 4. Tri thức (Knowledge Base); 5. Mức độ sử dụng AI (Usage Telemetry); 6. Kiểm toán dữ liệu (Audit Log); 7. Quản trị nền tảng (Admin Config).
B. Chỉ có 1 màn hình chat duy nhất, không có giao diện phê duyệt hay kiểm toán.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Design] Trải nghiệm tương tác cốt lõi trong phiên hội thoại AI là gì?
A. Streaming câu trả lời theo thời gian thực (SSE), hiển thị accordion trace các bước thực thi (Agent nào đang chạy, Tool nào được gọi, tham số và kết quả rút gọn), kèm nút đánh giá 👍/👎 cho từng câu trả lời.
B. Chỉ hiện câu trả lời khi mô hình hoàn thành toàn bộ sau vài chục giây mà không có streaming hay trace.
X. Khác (vui lòng nêu rõ)
[Answer]: A
