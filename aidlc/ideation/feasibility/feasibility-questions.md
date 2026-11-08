# Feasibility Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.
- [intent] `aidlc/ideation/intent-capture/intent-statement.md`
- [research] `aidlc/ideation/market-research/build-vs-buy.md`

## Q1. [Architect] Định hướng hạ tầng cơ sở dữ liệu và xác thực cho giai đoạn Production là gì?
A. PostgreSQL có Row-Level Security (RLS) làm lớp phòng thủ thứ hai, mã hóa các trường lương at-rest, tích hợp SSO doanh nghiệp chuẩn OIDC (Azure AD/Keycloak/Okta) kèm SCIM đồng bộ nhân sự từ HRIS.
B. Giữ SQLite cho môi trường nội bộ nhỏ, phân quyền thuần túy ở tầng ứng dụng (Python policy engine).
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Compliance] Yêu cầu tuân thủ pháp lý và quản trị dữ liệu áp dụng cho hệ thống là gì?
A. Tuân thủ nghiêm ngặt Nghị định 13/2023/NĐ-CP về bảo vệ dữ liệu cá nhân (DPIA), ký DPA với nhà cung cấp LLM về Zero Data Retention, chính sách tự động xóa hội thoại nhạy cảm C3 sau thời gian lưu trữ quy định (30 ngày), và ghi log kiểm toán minh bạch.
B. Chỉ cần tuân thủ bảo mật nội bộ cơ bản, không cần DPIA.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q3. [Architect] Chiến lược kết nối mô hình ngôn ngữ lớn (LLM Providers) và khả năng dự phòng (Resilience)?
A. Đa nhà cung cấp với trừu tượng hóa chuẩn Messages API: Mặc định Claude (prompt caching, streaming, tool calling), hỗ trợ adapter cho Gemini và OpenAI-compat (Groq, Ollama cục bộ), tích hợp cơ chế tự động retry theo Retry-After khi gặp mã lỗi 429 và server-side refusal fallback.
B. Chỉ kết nối một endpoint OpenAI duy nhất không có retry.
X. Khác (vui lòng nêu rõ)
[Answer]: A
