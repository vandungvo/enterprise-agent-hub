# Scope Definition Questions

## Sources
- [desc] Initial description: "Tài liệu hóa toàn diện hệ thống hiện tại (Brownfield Baseline từ Ideation, Reverse Engineering đến Ops)"
- [scope] Workflow-selected scope: `enterprise`.
- [intent] `aidlc/ideation/intent-capture/intent-statement.md`
- [feasibility] `aidlc/ideation/feasibility/feasibility-assessment.md`

## Q1. [Product] Các tính năng cốt lõi bắt buộc (Must-Have) trong phạm vi hiện tại (v1) là gì?
A. Trợ lý đa Agent (Router + 5 Domain Agents); Phân quyền dữ liệu ABAC tại data-tier; 16 công cụ nghiệp vụ gõ kiểu chặt; RAG lai BM25 + Embeddings có phân quyền tài liệu; Quy trình phê duyệt Human-in-the-loop; Giao diện Web đầy đủ 7 phân hệ; Adapter hỗ trợ đa LLM (Claude, Gemini, OpenAI-compat).
B. Chỉ làm chức năng chat RAG tài liệu văn bản, chưa tích hợp dữ liệu nghiệp vụ nhân sự hay tài chính.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q2. [Delivery] Chiến lược ưu tiên backlog (Prioritization Methodology)?
A. Áp dụng phương pháp MoSCoW kết hợp Risk-first: Ưu tiên bảo mật dữ liệu tuyệt đối (ABAC, K-anonymity, Masking log) làm nền móng trước, tiếp theo là Router & Domain Tools, RAG tri thức, và Hàng đợi phê duyệt.
B. Làm giao diện người dùng trước, phân quyền làm sau cùng.
X. Khác (vui lòng nêu rõ)
[Answer]: A

## Q3. [Product] Các tính năng nào được xếp vào lộ trình tương lai (Roadmap / Next Increment)?
A. Tích hợp SSO OIDC tập đoàn kèm SCIM đồng bộ nhân sự tự động; Chuyển đổi sang PostgreSQL có Row-Level Security; Kết nối ghi trực tiếp (write-back) vào ERP/SAP; Báo cáo định kỳ tự động qua email/chat; Red-team CI eval suite.
B. Không có kế hoạch phát triển thêm.
X. Khác (vui lòng nêu rõ)
[Answer]: A
