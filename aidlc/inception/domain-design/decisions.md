# Architecture Decision Records (ADR Log)

## ADR-01: Data-Tier Deterministic ABAC vs. Prompt-Tier Guardrails
- **Trạng thái**: Accepted
- **Bối cảnh**: LLM có thể bị đánh lừa qua các kỹ thuật Jailbreak hoặc Indirect Prompt Injection nếu việc phân quyền dựa vào system prompt.
- **Quyết định**: Toàn bộ quyết định phân quyền dữ liệu (Policy Decision Point) và thực thi (Policy Enforcement Point) nằm ở tầng mã Python trước khi truy vấn SQL. Model chỉ nhận được dữ liệu hợp lệ.
- **Hệ quả**: Triệt tiêu hoàn toàn nguy cơ rò rỉ dữ liệu mật qua prompt injection; tăng nhẹ thời gian xử lý (dưới 50ms per call) nhưng đảm bảo an toàn tuyệt đối.

## ADR-02: Multi-Agent Router Delegation vs. Monolithic Agent Prompt
- **Trạng thái**: Accepted
- **Bối cảnh**: Hệ thống có quá nhiều nghiệp vụ đa dạng (HR, Lương, Phép, Ngân sách, IT Helpdesk). Một prompt nguyên khối sẽ quá tải context window và làm giảm độ chính xác khi gọi 16 công cụ cùng lúc.
- **Quyết định**: Sử dụng Router Agent làm cửa tiếp nhận, phân tích ý định và ủy quyền cho 5 Agent chuyên môn qua tool `delegate_to_agent`.
- **Hệ quả**: Giảm kích thước context window, cô lập danh sách công cụ theo từng agent, tối ưu chi phí token qua Prompt Caching.

## ADR-03: Hybrid BM25 + Dense Embeddings with RRF vs. Pure Vector Search
- **Trạng thái**: Accepted
- **Bối cảnh**: Văn bản nội bộ doanh nghiệp bằng tiếng Việt thường chứa nhiều mã số văn bản, từ khóa chuyên ngành, số quyết định viết tắt mà mô hình vector embedding thông thường dễ bỏ sót.
- **Quyết định**: Kết hợp Lexical BM25 (xử lý tiếng Việt có dấu/không dấu) với Dense Vector Embeddings (FastEmbed) và trộn kết quả bằng Reciprocal Rank Fusion (RRF).
- **Hệ quả**: Độ chính xác tìm kiếm (recall & precision) cao vượt trội, trích dẫn chuẩn xác văn bản quy định.

## ADR-04: Human-in-the-Loop for Mutating Operations
- **Trạng thái**: Accepted
- **Bối cảnh**: Các hành động nộp đơn nghỉ phép, xin hoàn ứng chi phí tạo tác động trực tiếp đến quyền lợi và ngân sách tập đoàn.
- **Quyết định**: Tool không cập nhật trạng thái cuối cùng ngay lập tức mà tạo một bản ghi `approval_requests` với trạng thái `PENDING`, tự động định tuyến tới người quản lý có thẩm quyền theo quan hệ báo cáo tổ chức.
- **Hệ quả**: Đảm bảo quy trình quản trị doanh nghiệp, phòng chống tự động hóa sai lệch hoặc trục lợi.
