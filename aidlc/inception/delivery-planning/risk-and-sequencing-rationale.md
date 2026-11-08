# Risk and Sequencing Rationale

## 1. Why Risk-First Sequencing?
- **Phân quyền tại Data Tier là rủi ro sống còn**: Nếu xây dựng LLM router hoặc UI trước mà không có policy engine ở data tier, dự án sẽ đối mặt với nguy cơ rò rỉ dữ liệu lương C3 ngay trong các bản demo đầu tiên.
- Do đó, **Bolt 1 tập trung 100% vào U-01 (`core-security-policy`)** làm Walking Skeleton: kiểm chứng tính khả thi của ABAC, K-anonymity và log kiểm toán trước khi phát triển các tính năng tiếp theo.

## 2. Why Parallelize Bolt 2 (U-02 & U-04)?
- `U-02: data-access-tools` và `U-04: hybrid-rag-service` đều chỉ phụ thuộc vào `U-01` nhưng hoàn toàn độc lập với nhau.
- Hai luồng công việc này có thể được phát triển song song bởi Backend Dev và AI/RAG Engineer mà không xảy ra xung đột mã nguồn.

## 3. Why Sequence Bolt 3 Last?
- `U-03: multi-agent-orchestrator` cần các tools từ `U-02` và RAG service từ `U-04` để đăng ký vào prompt và schema của LLM.
- `U-05: web-portal-frontend` là tầng biểu diễn cuối cùng, chỉ hoàn thiện khi các API endpoint và SSE event streams của `U-03` đã ổn định.
