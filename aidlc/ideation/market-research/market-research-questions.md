# Market Research Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.
- [intent] `aidlc/ideation/intent-capture/intent-statement.md`

## Q1. [Product] Các giải pháp tương tự trên thị trường và khoảng trống công nghệ là gì?
A. Các giải pháp Enterprise AI thương mại (Glean, Moveworks, Microsoft Copilot Studio, AWS Q Business) cung cấp chatbot enterprise nhưng kiểm soát phân quyền chủ yếu ở tầng ứng dụng/prompt hoặc tích hợp hẹp với hệ sinh thái riêng, không hỗ trợ sâu mô hình ABAC nội bộ đa chi nhánh theo luật dữ liệu Việt Nam.
B. Doanh nghiệp chỉ có lựa chọn các SaaS CRM/ERP đóng gói.
C. Thị trường chưa có giải pháp nào về Trợ lý ảo cho doanh nghiệp.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Architect] Phân tích Build vs Buy: Tại sao lựa chọn tự phát triển (Build in-house)?
A. Cần toàn quyền kiểm soát tầng chính sách phân quyền dữ liệu (ABAC ở data tier), ngăn chặn triệt để prompt injection rò rỉ dữ liệu lương C3, độc lập không phụ thuộc duy nhất vào một nhà cung cấp LLM (hỗ trợ Claude, Gemini, Ollama), tuân thủ Nghị định 13/2023/NĐ-CP và lưu trữ dữ liệu tại chỗ.
B. Chi phí mua SaaS hàng tháng quá đắt so với chi phí phát triển nội bộ.
C. Thiếu giải pháp thương mại hỗ trợ ngôn ngữ tiếng Việt.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q3. [Product] Các xu hướng công nghệ AI chính yếu được áp dụng là gì?
A. Multi-agent orchestration (Router + Specialized Agents), Hybrid RAG (BM25 + Semantic Vector Embeddings + RRF), Human-in-the-loop cho các hành động có tác động, và K-Anonymity với complementary suppression cho phân tích tổng hợp.
B. Chỉ sử dụng Prompt Engineering cơ bản với một mô hình AI đơn lẻ.
C. Fine-tuning riêng một mô hình ngôn ngữ lớn từ đầu.
X. Khác (vui lòng nêu rõ)
[Answer]: A
