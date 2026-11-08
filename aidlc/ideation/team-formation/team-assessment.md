# Team Assessment & RACI Matrix

## Team Topology Overview
Dự án áp dụng mô hình Stream-aligned Team kết hợp Complicated-subsystem Team cho module Bảo mật dữ liệu & Phân quyền [Q1]:
- **Stream-aligned Squad**: Chịu trách nhiệm end-to-end các use-case người dùng (Chat, Phê duyệt, Tra cứu KB, UI Web) [Q1].
- **Core Security Focus**: Đảm bảo policy engine, thuật toán k-anonymity và data masking hoạt động chính xác tuyệt đối [Q1, Q2].

## RACI Matrix

| Hoạt động / Thành phần | Tech Lead (Architect) | AI/RAG Engineer | Fullstack Dev | Business Analyst | SecOps/DevOps | Lãnh đạo (CHRO/CFO) | Nguồn |
|---|---|---|---|---|---|---|---|
| **Định nghĩa Use case & Quy tắc chính sách** | C | I | I | **A / R** | I | C | [Q1] |
| **Kiến trúc ABAC & Policy Engine** | **A / R** | C | I | C | C | I | [Q1] |
| **Multi-Agent Runtime & LLM Adapters** | C | **A / R** | I | I | C | I | [Q1] |
| **Hybrid RAG & Vector Pipeline** | I | **A / R** | I | C | I | I | [Q1] |
| **Web UI & Streaming SSE Dashboard** | I | C | **A / R** | C | I | I | [Q1] |
| **Hạ tầng CI/CD, Docker & Đánh giá DPIA** | C | I | I | I | **A / R** | A | [Q1] |
| **Phê duyệt chính sách nghiệp vụ nhạy cảm** | I | I | I | C | I | **A** | [Q1] |

*Ghi chú: A = Accountable (Chịu trách nhiệm chính); R = Responsible (Người thực hiện); C = Consulted (Tham vấn); I = Informed (Nhận thông tin).*

## Assumptions & Open Questions
None. [Q1, Q2]
