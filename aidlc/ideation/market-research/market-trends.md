# Market Trends & Technology Directions

## Key Industry Trends
1. **Multi-Agent Systems vs Monolithic LLMs**: Thay vì một prompt khổng lồ giải quyết mọi việc, xu hướng hiện đại chuyển sang kiến trúc Router Agent và các Domain Agents chuyên biệt (HR, Finance, IT). Mô hình này giúp giảm context window, tăng độ chính xác của tool calling và cô lập rủi ro bảo mật [Q3].
2. **Deterministic Data-tier Security**: Cộng đồng kỹ thuật bảo mật AI toàn cầu nhận định prompt guardrails không thể chống đỡ 100% các cuộc tấn công prompt injection/jailbreak. Do đó, việc chuyển toàn bộ thẩm quyền phân quyền và tính toán dữ liệu xuống tầng code xác định (deterministic code tier) là hướng đi tiêu chuẩn cho hệ thống doanh nghiệp [Q1, Q2].
3. **Hybrid Search (BM25 + Dense Vectors)**: RAG đơn thuần dựa trên Vector thường bỏ sót các mã định danh, số quyết định, từ khóa viết tắt nội bộ. Kết hợp BM25 cho lexical search và Dense Vectors cho semantic search với thuật toán Reciprocal Rank Fusion (RRF) mang lại kết quả vượt trội cho văn bản tiếng Việt doanh nghiệp [Q3].
4. **Human-in-the-Loop (HITL) for High-Impact Actions**: Các hành động thay đổi trạng thái (nộp đơn nghỉ, xin hoàn ứng, tạo ticket) luôn có hàng đợi xác nhận và chuyển tiếp người duyệt theo quan hệ tổ chức để ngăn chặn tự động hóa ngoài tầm kiểm soát [Q3].

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
