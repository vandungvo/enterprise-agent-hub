# Intent Capture Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.

## Q1. [Product] Vấn đề nghiệp vụ cốt lõi mà Enterprise Agent Hub giải quyết là gì?
A. Hợp nhất trải nghiệm hỏi đáp và nghiệp vụ đa khối (HR, Tài chính, IT, Lãnh đạo) vào một giao diện chat duy nhất nhưng đảm bảo kiểm soát truy cập dữ liệu nghiêm ngặt ở tầng dữ liệu (ABAC).
B. Tự động hóa hoàn toàn quy trình phê duyệt nghỉ phép và chi phí mà không cần con người can thiệp.
C. Thay thế các phần mềm HRIS và ERP hiện có bằng chatbot AI.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Product] Đối tượng người dùng mục tiêu (Persona) và nhu cầu chính của họ là gì?
A. Đa dạng từ Nhân viên (tự phục vụ xem lương, ngày phép, IT), Quản lý (xem lịch vắng, số liệu team, duyệt đơn), Lãnh đạo/CEO (headcount, quỹ lương, ngân sách), đến HRBP, C&B, Tài chính, Quản trị hệ thống.
B. Chỉ tập trung cho nhân viên phòng ban Nhân sự (HR/C&B) thao tác nghiệp vụ.
C. Chỉ phục vụ Ban giám đốc và các cấp quản lý cấp cao xem báo cáo.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q3. [Product] Tiêu chí thành công và các chỉ số đo lường (Success Metrics) quan trọng nhất là gì?
A. Bảo mật dữ liệu tuyệt đối (0% rò rỉ lương/dữ liệu C3 qua prompt injection), sub-second policy evaluation, end-to-end streaming latency < 3s, ghi log kiểm toán 100% truy cập nhạy cảm.
B. Giảm 80% thời gian xử lý ticket IT và đơn nghỉ phép, tỷ lệ đánh giá hài lòng người dùng > 90%.
C. Cả hai mục tiêu trên: vừa đảm bảo an toàn phân quyền ở mức tuyệt đối vừa tối ưu trải nghiệm và hiệu suất vận hành.
X. Khác (vui lòng nêu rõ)
[Answer]: C

## Q4. [Product] Động lực/Tác nhân thúc đẩy sáng kiến này (Initiative Trigger) là gì?
A. Nhu cầu chuyển đổi số toàn diện cho tập đoàn đa ngành (Sao Mai Group), giải quyết bài toán dữ liệu phân mảnh và tuân thủ các quy định bảo vệ dữ liệu cá nhân (DPIA, Nghị định 13/2023/NĐ-CP).
B. Áp lực cắt giảm chi phí bản quyền phần mềm bên thứ ba.
C. Do sự cố rò rỉ dữ liệu trước đây yêu cầu siết chặt kiểm soát.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q5. [Product] Các bên liên quan chính (Key Stakeholders) và vai trò quyết định là gì?
A. Ban điều hành / CEO (phê duyệt chiến lược, ngân sách), CHRO & C&B (chính sách nhân sự, bảo mật lương), CFO (chính sách tài chính), Ban công nghệ & IT Admin (hạ tầng, mô hình LLM, chính sách kỹ thuật), Pháp chế/DPO (tuân thủ bảo vệ dữ liệu).
B. Chỉ có Trưởng phòng CNTT (CIO/IT Director) quyết định toàn bộ.
C. Ban quản lý dự án nội bộ.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q6. [Product] Phạm vi sản phẩm ở phiên bản v1 này: Những gì nằm ngoài phạm vi (Out of Scope)?
A. Không sử dụng Text-to-SQL trực tiếp vào DB nhân sự/tài chính; Không tự động thay đổi lương/chuyển tiền tài khoản mà không có quy trình nghiệp vụ; Chưa tích hợp ERP/SAP sâu dạng ghi trực tiếp (write-back tự động).
B. Không hỗ trợ truy cập trên thiết bị di động (chỉ dùng web desktop).
C. Không hỗ trợ nhà cung cấp LLM nào khác ngoài Claude.
X. Khác (vui lòng nêu rõ)
[Answer]: A
