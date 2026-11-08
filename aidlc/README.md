# AI-DLC Documentation Suite: Enterprise Agent Hub

Bộ tài liệu này được tạo theo chuẩn phương pháp luận **AI-DLC (AI-Driven Development Life Cycle)** từ `D:\02_Projects\aidlc-workflows` với cấu hình hồ sơ **Enterprise Profile** (toàn diện 5 Phase, 30 Stage), áp dụng cho hệ thống **Enterprise Agent Hub**.

> Demo trực tuyến: https://ent-agents.vercel.app · Tổng quan kỹ thuật và cách chạy: [README dự án](../README.md)

### ⭐ Tài liệu tham khảo chính (đọc trước)
- [`ba-guide.md`](ba-guide.md): Hướng dẫn cho Business Analyst: lộ trình công việc, kiến thức cần biết, bộ câu hỏi cho stakeholder, biểu mẫu.
- [`use-case-catalog.md`](ideation/scope-definition/use-case-catalog.md): Catalog use case toàn doanh nghiệp theo persona và phân loại dữ liệu, kèm lộ trình triển khai.
- [`permission-model.md`](construction/core-security-policy/nfr-design/permission-model.md): Mô hình phân quyền ABAC, các lớp kiểm soát, threat model, checklist production, đánh đổi đã biết.

---

## 🧭 Bản đồ Tài liệu & Cấu trúc Thư mục

### 0. State & Workflow Management
- [`aidlc-state.md`](aidlc-state.md): Trạng thái tiến trình vòng đời AI-DLC, theo dõi tiến độ từng stage.
- [`project-description.json`](project-description.json): Mô tả khởi tạo thẩm quyền của sáng kiến.

---

### 1. Phase 1: Ideation (Định hình & Thẩm định Sáng kiến)
- **1.1 Intent Capture & Framing**:
  - [`intent-capture-questions.md`](ideation/intent-capture/intent-capture-questions.md): Câu hỏi làm rõ vấn đề nghiệp vụ, persona, metric, ranh giới.
  - [`intent-statement.md`](ideation/intent-capture/intent-statement.md): Tuyên bố mục tiêu, bài toán giải quyết, chỉ số thành công.
  - [`stakeholder-map.md`](ideation/intent-capture/stakeholder-map.md): Bản đồ bên liên quan, ma trận quyền hạn và kênh truyền thông.
- **1.2 Market Research & Analysis**:
  - [`market-research-questions.md`](ideation/market-research/market-research-questions.md)
  - [`competitive-analysis.md`](ideation/market-research/competitive-analysis.md): So sánh với Microsoft Copilot, Glean, AWS Q Business.
  - [`build-vs-buy.md`](ideation/market-research/build-vs-buy.md): Phân tích chiến lược tự phát triển (Build in-house) để bảo vệ dữ liệu lương C3.
  - [`market-trends.md`](ideation/market-research/market-trends.md): Xu hướng Multi-Agent, Data-tier ABAC và Hybrid RAG.
- **1.3 Feasibility & Constraints**:
  - [`feasibility-questions.md`](ideation/feasibility/feasibility-questions.md)
  - [`feasibility-assessment.md`](ideation/feasibility/feasibility-assessment.md): Khả thi kỹ thuật, pháp lý (NĐ 13/2023/NĐ-CP, DPIA), kinh tế.
  - [`constraint-register.md`](ideation/feasibility/constraint-register.md): Danh mục ràng buộc kiến trúc, an toàn và vận hành.
  - [`raid-log.md`](ideation/feasibility/raid-log.md): Nhật ký Rủi ro, Giả định, Vấn đề và Phụ thuộc (RAID).
- **1.4 Scope Definition & Prioritization**:
  - [`scope-definition-questions.md`](ideation/scope-definition/scope-definition-questions.md)
  - [`scope-document.md`](ideation/scope-definition/scope-document.md): Ranh giới trong/ngoài phạm vi (In-scope vs Out-of-scope).
  - [`intent-backlog.md`](ideation/scope-definition/intent-backlog.md): Phân loại backlog theo MoSCoW.
  - [`use-case-catalog.md`](ideation/scope-definition/use-case-catalog.md): Catalog use case A–N theo persona, phân loại dữ liệu C1–C3, ưu tiên triển khai.
- **1.5 Team Formation & Collaboration**:
  - [`team-formation-questions.md`](ideation/team-formation/team-formation-questions.md)
  - [`team-assessment.md`](ideation/team-formation/team-assessment.md): Cấu trúc Squad và Ma trận RACI.
  - [`skill-matrix.md`](ideation/team-formation/skill-matrix.md): Đánh giá kỹ năng và khoảng trống năng lực.
  - [`mob-composition.md`](ideation/team-formation/mob-composition.md): Kế hoạch Mob Programming cho module bảo mật ABAC.
- **1.6 Rough Mockups & User Flow**:
  - [`rough-mockups-questions.md`](ideation/rough-mockups/rough-mockups-questions.md)
  - [`wireframes.md`](ideation/rough-mockups/wireframes.md): Khung giao diện phác thảo 7 phân hệ.
  - [`user-flow.md`](ideation/rough-mockups/user-flow.md): Sơ đồ trình tự tương tác chat có policy và hàng đợi phê duyệt.
- **1.7 Approval & Handoff**:
  - [`approval-handoff-questions.md`](ideation/approval-handoff/approval-handoff-questions.md)
  - [`initiative-brief.md`](ideation/approval-handoff/initiative-brief.md): Bản tóm tắt tổng hợp trình phê duyệt (Khuyến nghị: GO).
  - [`decision-log.md`](ideation/approval-handoff/decision-log.md): Nhật ký các quyết định chiến lược đã chốt.
- **Verification Gate 1**:
  - [`phase-check-ideation.md`](verification/phase-check-ideation.md): **PASSED**.

---

### 2. Phase 2: Inception (Khảo sát Kiến trúc & Phân rã Kỹ thuật)
- **2.1 Reverse Engineering (CodeKB Deliverables)**:
  - [`business-overview.md`](codekb/enterprise-agent-hub/business-overview.md): Tổng quan nghiệp vụ Sao Mai Group.
  - [`architecture.md`](codekb/enterprise-agent-hub/architecture.md): Kiến trúc hệ thống đa tầng và 9 lớp phòng ngự bảo mật.
  - [`code-structure.md`](codekb/enterprise-agent-hub/code-structure.md): Cây cấu trúc mã nguồn và trách nhiệm module.
  - [`api-documentation.md`](codekb/enterprise-agent-hub/api-documentation.md): Đặc tả API REST và SSE Streaming.
  - [`component-inventory.md`](codekb/enterprise-agent-hub/component-inventory.md): Danh mục 6 Agents và 16 Pydantic Typed Tools.
  - [`technology-stack.md`](codekb/enterprise-agent-hub/technology-stack.md): Ngôn ngữ, framework, RAG và LLMs.
  - [`dependencies.md`](codekb/enterprise-agent-hub/dependencies.md): Thư viện phụ thuộc và bản quyền phần mềm.
  - [`code-quality-assessment.md`](codekb/enterprise-agent-hub/code-quality-assessment.md): Đánh giá chất lượng (114/114 tests passed).
  - [`reverse-engineering-timestamp.md`](codekb/enterprise-agent-hub/reverse-engineering-timestamp.md)
- **2.2 Practices Discovery**:
  - [`team-practices.md`](inception/practices-discovery/team-practices.md): Thực hành lập trình và kiểm thử tự động.
  - [`discovered-rules.md`](inception/practices-discovery/discovered-rules.md): 4 quy tắc bất di bất dịch (Invariants).
  - [`evidence.md`](inception/practices-discovery/evidence.md): Dẫn chứng mã nguồn cho từng quy tắc.
- **2.3 Requirements Analysis**:
  - [`requirements.md`](inception/requirements-analysis/requirements.md): 10 Functional Requirements (FR-01..10) và 5 Non-Functional Requirements (NFR-01..05).
  - [`traceability.json`](inception/requirements-analysis/traceability.json)
- **2.4 User Stories**:
  - [`personas.md`](inception/user-stories/personas.md): 7 Personas người dùng chi tiết.
  - [`stories.md`](inception/user-stories/stories.md): 6 User Stories cốt lõi kèm tiêu chí Gherkin.
  - [`user-stories-assessment.md`](inception/user-stories/user-stories-assessment.md)
- **2.5 Refined Mockups**:
  - [`mockups.md`](inception/refined-mockups/mockups.md): Bố cục chi tiết, luồng tương tác và checklist tiếp cận WCAG 2.1 AA.
- **2.6 Domain Design**:
  - [`components.md`](inception/domain-design/components.md): Sơ đồ Domain và đặc tả YAML 6 components.
  - [`decisions.md`](inception/domain-design/decisions.md): 9 Architecture Decision Records (ADR-01..09), gồm hosting Vercel, token stateless ký HMAC, PostgreSQL dùng chung, production hardening và cấu trúc package theo domain.
- **2.7 Units Generation**:
  - [`unit-of-work.md`](inception/units-generation/unit-of-work.md): Phân rã 5 Units (U-01..U-05).
  - [`unit-of-work-dependency.md`](inception/units-generation/unit-of-work-dependency.md): Đồ thị phụ thuộc DAG.
  - [`unit-of-work-story-map.md`](inception/units-generation/unit-of-work-story-map.md): Ánh xạ Story Map.
- **2.8 Contract Design**:
  - [`contract-summary.md`](inception/contract-design/contract-summary.md): Hợp đồng giao tiếp giữa các Units, REST API và SSE streams.
- **2.9 Delivery Planning**:
  - [`bolt-plan.md`](inception/delivery-planning/bolt-plan.md): Kế hoạch 3 đợt triển khai (Bolts) theo nguyên tắc Risk-First.
  - [`team-allocation.md`](inception/delivery-planning/team-allocation.md): Phân bổ nhân sự theo từng Bolt.
  - [`risk-and-sequencing-rationale.md`](inception/delivery-planning/risk-and-sequencing-rationale.md)
  - [`external-dependency-map.md`](inception/delivery-planning/external-dependency-map.md)
- **Verification Gate 2**:
  - [`phase-check-inception.md`](verification/phase-check-inception.md): **PASSED**.

---

### 3. Phase 3: Construction (Thiết kế Chi tiết & Kiểm thử Tích hợp)
- **Per-Unit Specifications**:
  - [`core-security-policy/functional-spec.md`](construction/core-security-policy/functional-design/functional-spec.md): Đặc tả phân quyền ABAC, thuật toán k-anonymity và complementary suppression.
  - [`core-security-policy/security-design.md`](construction/core-security-policy/nfr-design/security-design.md): Thiết kế chống prompt injection và lược đồ log kiểm toán.
  - [`core-security-policy/permission-model.md`](construction/core-security-policy/nfr-design/permission-model.md): Mô hình phân quyền đầy đủ: Principal, phân loại dữ liệu, các lớp kiểm soát, threat model, checklist production.
  - [`core-security-policy/code-summary.md`](construction/core-security-policy/code-generation/code-summary.md)
  - [`data-access-tools/code-summary.md`](construction/data-access-tools/code-generation/code-summary.md): Tổng kết 16 Typed Tools.
  - [`multi-agent-orchestrator/code-summary.md`](construction/multi-agent-orchestrator/code-generation/code-summary.md): Runtime điều phối, router delegation và LLM adapters.
  - [`hybrid-rag-service/code-summary.md`](construction/hybrid-rag-service/code-generation/code-summary.md): RAG tiếng Việt lai và lọc Document ACL.
  - [`web-portal-frontend/code-summary.md`](construction/web-portal-frontend/code-generation/code-summary.md): Frontend 7 phân hệ.
- **Build, Test & CI Pipeline**:
  - [`build-instructions.md`](construction/build-and-test/build-instructions.md): Hướng dẫn cài đặt, cấu hình `.env` và khởi chạy server.
  - [`test-results.md`](construction/build-and-test/test-results.md): Kết quả kiểm thử tự động (114/114 trên SQLite và PostgreSQL), kiểm thử đa instance và smoke test production.
  - [`ci-config.md`](construction/ci-pipeline/ci-config.md): Cấu hình GitHub Actions CI Workflow.
  - [`quality-gates.md`](construction/ci-pipeline/quality-gates.md): 5 Tiêu chuẩn kiểm soát chất lượng khi merge code.
- **Verification Gate 3**:
  - [`phase-check-construction.md`](verification/phase-check-construction.md): **PASSED**.

---

### 4. Phase 4: Operation (Triển khai, Giám sát & Vận hành Bền vững)
- **Deployment & Resilience**:
  - [`deployment-strategy.md`](operation/deployment-pipeline/deployment-strategy.md): Deploy Vercel Serverless hiện tại (`api/index.py`, `vercel.json`, biến môi trường, giới hạn) và mục tiêu production (container, PostgreSQL, Rolling Update).
  - [`rollback-runbook.md`](operation/deployment-pipeline/rollback-runbook.md): Quy trình Rollback khẩn cấp (`vercel rollback` / `promote`, Kubernetes), rollback policy, thu hồi phiên, ghi nhận sự cố 2026-11-09.
- **Observability & SLO**:
  - [`dashboards.md`](operation/observability-setup/dashboards.md): Bảng điều khiển giám sát Telemetry và Audit.
  - [`alarms.md`](operation/observability-setup/alarms.md): Ngưỡng cảnh báo sự cố bảo mật, mã lỗi 429 và độ trễ.
  - [`slo-config.md`](operation/observability-setup/slo-config.md): Cam kết chất lượng dịch vụ (SLO: 99.9% uptime, 0% rò rỉ C3).
- **Incident Response**:
  - [`runbooks.md`](operation/incident-response/runbooks.md): Hướng dẫn xử lý lỗi 429, hot-switch model và điều tra rò rỉ dữ liệu.
  - [`escalation-matrix.md`](operation/incident-response/escalation-matrix.md): Ma trận phân cấp leo thang sự cố (SEV-1 đến SEV-4).
- **Optimization & Continuous Learning**:
  - [`cost-analysis.md`](operation/feedback-optimization/cost-analysis.md): Phân tích hiệu quả chi phí token nhờ Prompt Caching (tiết kiệm ~70%).
  - [`feedback-loop.md`](operation/feedback-optimization/feedback-loop.md): Vòng lặp cải tiến liên tục từ đánh giá 👍/👎 của người dùng.
