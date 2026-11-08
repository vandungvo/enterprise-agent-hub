# Requirements Analysis Questions

## Sources
- [codekb] `aidlc/codekb/enterprise-agent-hub/`
- [intent] `aidlc/ideation/intent-capture/intent-statement.md`
- [scope] `aidlc/ideation/scope-definition/scope-document.md`

## Q1. [Product] Nhóm yêu cầu chức năng cốt lõi (Functional Requirements) bao gồm những mảng nào?
A. 1. Trợ lý hội thoại thông minh đa agent; 2. Phân quyền dữ liệu ABAC thời gian thực; 3. Tra cứu thông tin cá nhân & Lương C3; 4. Quản lý ngày phép & Lịch vắng mặt; 5. Phân tích nhân sự & Quỹ lương cho lãnh đạo; 6. Quản lý chi phí & Đề nghị thanh toán; 7. Hỗ trợ IT & Quản lý ticket; 8. Tra cứu tri thức RAG lai có bảo mật; 9. Hàng đợi phê duyệt Human-in-the-loop; 10. Bảng điều khiển quản trị & Kiểm toán.
B. Chỉ cần chức năng chat cơ bản và tìm kiếm tài liệu thông thường.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Architect] Nhóm yêu cầu phi chức năng (Non-Functional Requirements) trọng tâm là gì?
A. 1. Bảo mật: Tuyệt đối không rò rỉ dữ liệu C3, zero prompt injection leak, che mờ log C3; 2. Hiệu năng: Phản hồi streaming SSE < 3s, đánh giá policy < 50ms; 3. Độ tin cậy: Tự động retry 429 backoff, fallback đa nhà cung cấp LLM; 4. Tuân thủ: DPIA, Nghị định 13/2023/NĐ-CP, xóa hội thoại C3 sau 30 ngày.
B. Không có yêu cầu khắt khe về thời gian phản hồi hay bảo mật.
X. Khác (vui lòng nêu rõ)
[Answer]: A
