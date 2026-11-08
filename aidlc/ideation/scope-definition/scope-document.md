# Scope Document

## In-Scope Capabilities (Baseline v1)

### 1. Multi-Agent Orchestration & Runtime
- **Router Agent ("Trợ lý Sao Mai")**: Nhận câu hỏi tự nhiên từ người dùng, phân tích ý định và ủy quyền (delegate) câu hỏi tới agent nghiệp vụ phù hợp qua tool `delegate_to_agent` [Q1].
- **5 Domain Agents chuyên biệt**:
  - `people`: Hồ sơ cá nhân, phiếu lương, lịch sử lương, số dư phép, nộp đơn nghỉ, lịch vắng team, chính sách nhân sự [Q1].
  - `insights`: Headcount, tỷ lệ tuyển mới/nghỉ việc, phân tích quỹ lương, báo cáo ngân sách với k-anonymity [Q1].
  - `finance`: Chính sách công tác phí, hoàn ứng, nộp đề nghị thanh toán, theo dõi ngân sách [Q1].
  - `it_helpdesk`: Hướng dẫn tài khoản, VPN, email, cấp phát thiết bị, tạo ticket hỗ trợ [Q1].
  - `company_info`: Giới thiệu tập đoàn, sơ đồ tổ chức, danh bạ nhân sự, nội quy [Q1].
- **Hỗ trợ Streaming SSE**: Trả về token hội thoại thời gian thực kèm telemetry trace các bước gọi tool [Q1].

### 2. ABAC Data-Tier Security & Policy Engine
- **Principal Reconstruction**: Tái tạo thông tin danh tính (đơn vị, tuyến báo cáo, cấp bậc, vai trò) tại mỗi HTTP request từ DB [Q1, feasibility].
- **Centralized Policies (`policies.yaml`)**: Phân quyền chi tiết theo từng resource (`compensation.individual`, `leave.calendar`, `finance.budget`,...) với các scope: `self`, `direct_reports`, `subtree`, `same_unit`, `role_scope` [Q1].
- **Bảo vệ số liệu tổng hợp**: K-anonymity (k=5 hoặc k=3) và Complementary Suppression (ẩn thêm nhóm nhỏ thứ hai để chống suy ngược bằng phép trừ tổng) [Q1, Q2].
- **Che mờ log (Log Masking)**: Kết quả của các tool trả về dữ liệu C3 (lương, bảo hiểm) tự động bị che khi ghi log vận hành [Q1].

### 3. Knowledge Base & Hybrid RAG
- 5 Knowledge Base độc lập: Thông tin tập đoàn, Chính sách nhân sự, IT Helpdesk, Quy định tài chính, Tài liệu lãnh đạo [Q1].
- RAG lai: BM25 Lexical + FastEmbed Dense Vectors, trộn kết quả bằng Reciprocal Rank Fusion (RRF) tối ưu hóa cho tiếng Việt có/không dấu [Q1].
- Document ACL: Kiểm soát quyền đọc từng tài liệu theo `roles`, `units`, `min_level` [Q1].

### 4. Human-in-the-Loop Approval Queue
- Hàng đợi phê duyệt cho các hành động thay đổi trạng thái: Nộp đơn nghỉ phép, Đề nghị thanh toán, Tạo ticket IT [Q1].
- Định tuyến người duyệt thông minh theo quan hệ báo cáo quản lý (`manager_id`) và hạn mức chi phí (> 20 triệu chuyển lên Trưởng khối) [Q1].

### 5. Web Frontend & Telemetry Dashboard
- 7 phân hệ giao diện: Chat, Hàng đợi phê duyệt, Quyền của tôi ("Ai đã xem dữ liệu của tôi"), Duyệt tri thức KB, Mức độ sử dụng AI & Chi phí token, Kiểm toán truy cập dữ liệu nhạy cảm, Quản trị hệ thống [Q1].

### 6. LLM Provider Flexibility
- Tích hợp chuẩn Anthropic Messages API (Claude), adapter cho Google Gemini và OpenAI Chat Completions (Groq, Ollama, LM Studio, OpenRouter) [Q1].

---

## Out-of-Scope (Deferred to Future Increments)
- Ghi trực tiếp (Write-back) không qua kiểm soát vào hệ thống ERP SAP / Oracle [Q3].
- Phân tích Text-to-SQL tự do trên cơ sở dữ liệu [intent, Q3].
- Tính toán phân tích vi phân tự động (Differential Privacy) đa phiên [feasibility, Q3].
- Ứng dụng di động độc lập (Native iOS/Android App) [Q3].

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
