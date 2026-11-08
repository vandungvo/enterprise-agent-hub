# RAID Log (Risks, Assumptions, Issues, Dependencies)

## 1. Risks

| Risk ID | Description | Impact | Probability | Mitigation Strategy | Owner | Source |
|---|---|---|---|---|---|---|
| R-01 | Tấn công Prompt Injection cố tình mạo danh lãnh đạo hoặc trích xuất lương người khác | High | Medium | Thực thi phân quyền ABAC ở data tier trước khi truy vấn dữ liệu; danh tính lấy từ session thay vì prompt | Architect / Security | [intent] |
| R-02 | Nhà cung cấp LLM gặp sự cố quá tải, trả mã 429 Rate Limit | Medium | High | Adapter hỗ trợ Exponential Backoff theo header `Retry-After`; tích hợp fallback sang nhà cung cấp phụ (Gemini, Ollama) | Backend Lead | [Q3] |
| R-03 | Suy ngược dữ liệu qua các lần truy vấn số liệu tổng hợp liên tiếp (differencing attacks) | High | Low | Áp dụng K-anonymity và complementary suppression; thiết lập rate limit và cảnh báo truy vấn bất thường | Security / Data | [intent] |
| R-04 | Rủi ro pháp lý về việc truyền dữ liệu qua API ra ngoài lãnh thổ Việt Nam | High | Low | Triển khai mô hình hợp đồng DPA với Zero Data Retention; chuẩn bị phương án LLM tự host (Ollama / vLLM) trong nước | Legal / Architect | [Q2] |

## 2. Assumptions

| Assumption ID | Description | Validation Status | Source |
|---|---|---|---|
| A-01 | Dữ liệu sơ đồ tổ chức, quan hệ báo cáo `manager_id` trong HRIS luôn được cập nhật chính xác và kịp thời | Confirmed qua cấu trúc bảng HRIS demo | [intent, Q1] |
| A-02 | Doanh nghiệp sở hữu hạ tầng mạng an toàn và sẵn sàng cung cấp kết nối mạng tới LLM endpoints được phê duyệt | Confirmed | [Q3] |

## 3. Issues

| Issue ID | Description | Current Status | Resolution Plan | Source |
|---|---|---|---|---|
| I-01 | Bản demo trên Vercel từng dùng SQLite per-instance (hội thoại, phê duyệt lúc hiện lúc mất) | Resolved (2026-11-09) | Token stateless ký HMAC (ADR-06) + PostgreSQL dùng chung cho mọi trạng thái (ADR-07). Còn lại cho production: SSO OIDC, Alembic migration | [Q1] |
| I-02 | K-anonymity hiện tại áp dụng trên từng truy vấn đơn lẻ; chưa chống suy ngược qua nhiều truy vấn liên tiếp kéo dài | Planned | Bổ sung giới hạn tần suất truy vấn nhạy cảm và cơ chế diffing protection | [intent] |

## 4. Dependencies

| Dependency ID | External / Internal Dependency | Criticality | Impacted Area | Source |
|---|---|---|---|---|
| D-01 | Nhà cung cấp LLM (Anthropic Claude API / Google Gemini API) | Critical | Trợ lý hội thoại & Streaming phản hồi | [Q3] |
| D-02 | Hệ thống HRIS & Core Database nội bộ | Critical | Dữ liệu nhân sự, cơ cấu tổ chức, phân quyền Principal | [Q1] |
| D-03 | Cổng xác thực tập đoàn (SSO Identity Provider) | High | Đăng nhập và xác thực danh tính người dùng | [Q1] |

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
