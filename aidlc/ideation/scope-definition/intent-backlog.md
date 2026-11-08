# Intent Backlog (MoSCoW Prioritization)

## 1. Must-Have (M) - Nền tảng cốt lõi bắt buộc hoàn thành trong v1

| ID | Capability / Work Unit | Mô tả | Trạng thái hiện tại | Nguồn |
|---|---|---|---|---|
| M-01 | **Security & Policy Engine (ABAC)** | Xây dựng bộ máy kiểm tra quyền hạn trước mọi truy vấn dữ liệu; tái dựng Principal từ HRIS mỗi request. | Hoàn thành ✅ | [Q1, Q2] |
| M-02 | **Multi-Agent Orchestration & Runtime** | Xây dựng Router agent và runtime quản lý hội thoại streaming, tool dispatch, error fallback. | Hoàn thành ✅ | [Q1] |
| M-03 | **16 Typed Pydantic Tools** | Cung cấp các công cụ truy xuất dữ liệu có kiểu chặt chẽ cho 5 mảng nghiệp vụ (HR, Finance, Analytics, IT, Org). | Hoàn thành ✅ | [Q1] |
| M-04 | **K-Anonymity & Anti-Inference** | Thuật toán bảo vệ số liệu tổng hợp lương/nhân sự (k=3, k=5) kèm Complementary Suppression. | Hoàn thành ✅ | [Q1, Q2] |
| M-05 | **Vietnamese Hybrid RAG** | Tìm kiếm văn bản lai BM25 + Embeddings kết hợp lọc bảo mật ACL từng tài liệu. | Hoàn thành ✅ | [Q1] |
| M-06 | **Approval Queue (HITL)** | Hàng đợi phê duyệt cho đơn nghỉ phép, thanh toán, ticket IT theo tuyến báo cáo tổ chức. | Hoàn thành ✅ | [Q1] |
| M-07 | **Multi-LLM Adapters** | Tầng dịch giao thức hỗ trợ Claude, Gemini, OpenAI-compat và Ollama tự động retry. | Hoàn thành ✅ | [Q1] |
| M-08 | **Web Portal & Telemetry** | Giao diện Web 7 phân hệ phục vụ chat, phê duyệt, quản lý quyền, tra cứu KB và đo lường sử dụng. | Hoàn thành ✅ | [Q1] |

## 2. Should-Have (S) - Nâng cao cho môi trường Production

| ID | Capability / Work Unit | Mô tả | Trạng thái | Nguồn |
|---|---|---|---|---|
| S-01 | **Enterprise SSO OIDC & SCIM** | Tích hợp Azure AD / Keycloak và SCIM đồng bộ nhân sự từ HRIS tự động. | Roadmap 🔜 | [Q3] |
| S-02 | **PostgreSQL RLS Migration** | Chuyển đổi từ SQLite demo sang PostgreSQL với Row-Level Security và mã hóa dữ liệu at-rest. | Roadmap 🔜 | [Q3] |
| S-03 | **Red-team CI Evaluation** | Bộ kiểm thử tự động đánh giá khả năng chống prompt injection và rò rỉ dữ liệu trước mỗi lần đổi model/prompt. | Roadmap 🔜 | [Q3] |
| S-04 | **Differencing Protection** | Giới hạn tần suất và thuật toán phát hiện các đợt truy vấn trừ tổng liên tiếp nhiều lần. | Roadmap 🔜 | [Q3] |

## 3. Could-Have (C) - Tiện ích bổ sung

| ID | Capability / Work Unit | Mô tả | Trạng thái | Nguồn |
|---|---|---|---|---|
| C-01 | **Scheduled Executive Reports** | Tự động sinh báo cáo tổng quan nhân sự/tài chính hằng tuần gửi email Ban điều hành. | Roadmap 🔜 | [Q3] |
| C-02 | **Salary Net Estimator** | Công cụ tính toán mô phỏng lương thực nhận khi thay đổi người phụ thuộc. | Roadmap 🔜 | [Q3] |

## 4. Won't-Have (W) - Loại trừ khỏi phạm vi hiện tại

| ID | Feature | Lý do loại trừ | Nguồn |
|---|---|---|---|
| W-01 | **Direct Text-to-SQL on Core DB** | Rủi ro bảo mật quá lớn, không thể kiểm soát chặt chẽ bằng ABAC policy. | [intent, Q1] |
| W-02 | **Unsupervised ERP Write-back** | Các giao dịch tài chính/nhân sự bắt buộc phải có kiểm tra và phê duyệt của con người. | [intent, Q3] |

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
