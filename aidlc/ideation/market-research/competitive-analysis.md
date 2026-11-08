# Competitive Analysis & Market Assessment

## Market Landscape Overview
Trong phân khúc trợ lý AI cho môi trường doanh nghiệp (Enterprise AI Assistant & Knowledge Discovery), các giải pháp phổ biến bao gồm [Q1]:
1. **Microsoft 365 Copilot / Copilot Studio**: Tích hợp sâu Microsoft Graph, phù hợp hệ sinh thái Azure/Office 365 nhưng khó tùy biến logic ABAC phi cấu trúc ngoài Microsoft và phụ thuộc hoàn toàn vào hệ sinh thái Azure OpenAI.
2. **Glean / Moveworks**: Khả năng enterprise search và agentic workflows tốt, nhưng chi phí bản quyền SaaS rất cao, lưu trữ dữ liệu tại cloud của nhà cung cấp, và không hỗ trợ các quy định bảo mật riêng biệt tại thị trường Việt Nam (Nghị định 13/2023/NĐ-CP).
3. **AWS Q Business**: Phù hợp cho hạ tầng AWS nhưng hạn chế trong việc tùy biến multi-agent router tùy biến và chính sách k-anonymity đặc thù cho bảng lương tập đoàn.

## Feature Comparison Matrix

| Tiêu chí so sánh | Microsoft Copilot | Glean | AWS Q Business | **Enterprise Agent Hub (Sao Mai)** | Nguồn |
|---|---|---|---|---|---|
| **Mô hình triển khai** | SaaS Cloud (Azure) | SaaS Cloud | Managed AWS | Tự chủ hạ tầng (On-premise / Private VPC) | [Q1, Q2] |
| **Cơ chế phân quyền** | RBAC tầng ứng dụng & Graph | RBAC + Connector ACL | IAM / Identity Center | **ABAC tại tầng truy cập dữ liệu (Data-tier engine)** | [Q1, Q2] |
| **Bảo vệ dữ liệu nhạy cảm C3 (Lương)** | Phụ thuộc prompt guardrail | Lọc văn bản | Lọc văn bản | **Không Text-to-SQL, Tool gõ kiểu chặt + Masking log + k-anonymity** | [Q1, Q2] |
| **Nhà cung cấp LLM** | OpenAI độc quyền | Đóng gói | Bedrock (Anthropic/Titan) | **Đa LLM (Claude, Gemini, OpenAI-compat, Ollama)** | [Q2] |
| **Quy trình phê duyệt (HITL)** | Tích hợp PowerAutomate | Webhook | Chưa hỗ trợ sâu | **Tích hợp sẵn hàng đợi duyệt theo tuyến báo cáo nhân sự** | [Q3] |
| **Tối ưu hóa tiếng Việt** | Tiêu chuẩn | Tiêu chuẩn | Hạn chế | **RAG lai BM25 + Vector tokenization tiếng Việt có/không dấu** | [Q3] |

## Strategic Differentiation
- **Data-tier Policy Enforcement**: Phân quyền không nằm trong system prompt mà được kiểm tra bằng code Python trước khi truy vấn dữ liệu. Không một prompt injection nào có thể mở rộng quyền của người dùng [Q1, Q2].
- **K-Anonymity & Complementary Suppression**: Ngăn chặn hoàn toàn các kỹ thuật suy ngược số liệu lương/nhân sự của các nhóm nhỏ [Q3].
- **Zero-lockin Multi-Provider Architecture**: Cho phép chuyển đổi linh hoạt giữa Claude 3.5/Opus, Gemini 1.5/2.0 và LLM mã nguồn mở nội bộ (Ollama) [Q2].

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
