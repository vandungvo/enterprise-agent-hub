# AI-DLC Documentation Suite: Enterprise Agent Hub

Bộ tài liệu này được tạo theo chuẩn phương pháp luận **AI-DLC (AI-Driven Development Life Cycle)** từ `D:\02_Projects\aidlc-workflows` với cấu hình hồ sơ **Enterprise Profile** (toàn diện 5 Phase, 30 Stage), áp dụng cho hệ thống **Enterprise Agent Hub**.

---

## 🧭 Bản đồ Tài liệu & Cấu trúc Thư mục

### 0. State & Workflow Management
- [`aidlc-state.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/aidlc-state.md): Trạng thái tiến trình vòng đời AI-DLC, theo dõi tiến độ từng stage.
- [`project-description.json`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/project-description.json): Mô tả khởi tạo thẩm quyền của sáng kiến.

---

### 1. Phase 1: Ideation (Định hình & Thẩm định Sáng kiến)
- **1.1 Intent Capture & Framing**:
  - [`intent-capture-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/intent-capture/intent-capture-questions.md): Câu hỏi làm rõ vấn đề nghiệp vụ, persona, metric, ranh giới.
  - [`intent-statement.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/intent-capture/intent-statement.md): Tuyên bố mục tiêu, bài toán giải quyết, chỉ số thành công.
  - [`stakeholder-map.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/intent-capture/stakeholder-map.md): Bản đồ bên liên quan, ma trận quyền hạn và kênh truyền thông.
- **1.2 Market Research & Analysis**:
  - [`market-research-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/market-research/market-research-questions.md)
  - [`competitive-analysis.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/market-research/competitive-analysis.md): So sánh với Microsoft Copilot, Glean, AWS Q Business.
  - [`build-vs-buy.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/market-research/build-vs-buy.md): Phân tích chiến lược tự phát triển (Build in-house) để bảo vệ dữ liệu lương C3.
  - [`market-trends.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/market-research/market-trends.md): Xu hướng Multi-Agent, Data-tier ABAC và Hybrid RAG.
- **1.3 Feasibility & Constraints**:
  - [`feasibility-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/feasibility/feasibility-questions.md)
  - [`feasibility-assessment.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/feasibility/feasibility-assessment.md): Khả thi kỹ thuật, pháp lý (NĐ 13/2023/NĐ-CP, DPIA), kinh tế.
  - [`constraint-register.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/feasibility/constraint-register.md): Danh mục ràng buộc kiến trúc, an toàn và vận hành.
  - [`raid-log.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/feasibility/raid-log.md): Nhật ký Rủi ro, Giả định, Vấn đề và Phụ thuộc (RAID).
- **1.4 Scope Definition & Prioritization**:
  - [`scope-definition-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/scope-definition/scope-definition-questions.md)
  - [`scope-document.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/scope-definition/scope-document.md): Ranh giới trong/ngoài phạm vi (In-scope vs Out-of-scope).
  - [`intent-backlog.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/scope-definition/intent-backlog.md): Phân loại backlog theo MoSCoW.
- **1.5 Team Formation & Collaboration**:
  - [`team-formation-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/team-formation/team-formation-questions.md)
  - [`team-assessment.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/team-formation/team-assessment.md): Cấu trúc Squad và Ma trận RACI.
  - [`skill-matrix.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/team-formation/skill-matrix.md): Đánh giá kỹ năng và khoảng trống năng lực.
  - [`mob-composition.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/team-formation/mob-composition.md): Kế hoạch Mob Programming cho module bảo mật ABAC.
- **1.6 Rough Mockups & User Flow**:
  - [`rough-mockups-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/rough-mockups/rough-mockups-questions.md)
  - [`wireframes.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/rough-mockups/wireframes.md): Khung giao diện phác thảo 7 phân hệ.
  - [`user-flow.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/rough-mockups/user-flow.md): Sơ đồ trình tự tương tác chat có policy và hàng đợi phê duyệt.
- **1.7 Approval & Handoff**:
  - [`approval-handoff-questions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/approval-handoff/approval-handoff-questions.md)
  - [`initiative-brief.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/approval-handoff/initiative-brief.md): Bản tóm tắt tổng hợp trình phê duyệt (Khuyến nghị: GO).
  - [`decision-log.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/ideation/approval-handoff/decision-log.md): Nhật ký các quyết định chiến lược đã chốt.
- **Verification Gate 1**:
  - [`phase-check-ideation.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/verification/phase-check-ideation.md): **PASSED**.

---

### 2. Phase 2: Inception (Khảo sát Kiến trúc & Phân rã Kỹ thuật)
- **2.1 Reverse Engineering (CodeKB Deliverables)**:
  - [`business-overview.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/business-overview.md): Tổng quan nghiệp vụ Sao Mai Group.
  - [`architecture.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/architecture.md): Kiến trúc hệ thống đa tầng và 9 lớp phòng ngự bảo mật.
  - [`code-structure.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/code-structure.md): Cây cấu trúc mã nguồn và trách nhiệm module.
  - [`api-documentation.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/api-documentation.md): Đặc tả API REST và SSE Streaming.
  - [`component-inventory.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/component-inventory.md): Danh mục 6 Agents và 16 Pydantic Typed Tools.
  - [`technology-stack.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/technology-stack.md): Ngôn ngữ, framework, RAG và LLMs.
  - [`dependencies.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/dependencies.md): Thư viện phụ thuộc và bản quyền phần mềm.
  - [`code-quality-assessment.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/code-quality-assessment.md): Đánh giá chất lượng (47/47 tests passed).
  - [`reverse-engineering-timestamp.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/codekb/enterprise-agent-hub/reverse-engineering-timestamp.md)
- **2.2 Practices Discovery**:
  - [`team-practices.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/practices-discovery/team-practices.md): Thực hành lập trình và kiểm thử tự động.
  - [`discovered-rules.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/practices-discovery/discovered-rules.md): 4 quy tắc bất di bất dịch (Invariants).
  - [`evidence.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/practices-discovery/evidence.md): Dẫn chứng mã nguồn cho từng quy tắc.
- **2.3 Requirements Analysis**:
  - [`requirements.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/requirements-analysis/requirements.md): 10 Functional Requirements (FR-01..10) và 5 Non-Functional Requirements (NFR-01..05).
  - [`traceability.json`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/requirements-analysis/traceability.json)
- **2.4 User Stories**:
  - [`personas.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/user-stories/personas.md): 7 Personas người dùng chi tiết.
  - [`stories.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/user-stories/stories.md): 6 User Stories cốt lõi kèm tiêu chí Gherkin.
  - [`user-stories-assessment.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/user-stories/user-stories-assessment.md)
- **2.5 Refined Mockups**:
  - [`mockups.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/refined-mockups/mockups.md): Bố cục chi tiết, luồng tương tác và checklist tiếp cận WCAG 2.1 AA.
- **2.6 Domain Design**:
  - [`components.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/domain-design/components.md): Sơ đồ Domain và đặc tả YAML 6 components.
  - [`decisions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/domain-design/decisions.md): 4 Architecture Decision Records (ADR-01..04).
- **2.7 Units Generation**:
  - [`unit-of-work.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/units-generation/unit-of-work.md): Phân rã 5 Units (U-01..U-05).
  - [`unit-of-work-dependency.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/units-generation/unit-of-work-dependency.md): Đồ thị phụ thuộc DAG.
  - [`unit-of-work-story-map.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/units-generation/unit-of-work-story-map.md): Ánh xạ Story Map.
- **2.8 Contract Design**:
  - [`contract-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/contract-design/contract-summary.md): Hợp đồng giao tiếp giữa các Units, REST API và SSE streams.
- **2.9 Delivery Planning**:
  - [`bolt-plan.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/delivery-planning/bolt-plan.md): Kế hoạch 3 đợt triển khai (Bolts) theo nguyên tắc Risk-First.
  - [`team-allocation.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/delivery-planning/team-allocation.md): Phân bổ nhân sự theo từng Bolt.
  - [`risk-and-sequencing-rationale.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/delivery-planning/risk-and-sequencing-rationale.md)
  - [`external-dependency-map.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/inception/delivery-planning/external-dependency-map.md)
- **Verification Gate 2**:
  - [`phase-check-inception.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/verification/phase-check-inception.md): **PASSED**.

---

### 3. Phase 3: Construction (Thiết kế Chi tiết & Kiểm thử Tích hợp)
- **Per-Unit Specifications**:
  - [`core-security-policy/functional-spec.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/core-security-policy/functional-design/functional-spec.md): Đặc tả phân quyền ABAC, thuật toán k-anonymity và complementary suppression.
  - [`core-security-policy/security-design.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/core-security-policy/nfr-design/security-design.md): Thiết kế chống prompt injection và lược đồ log kiểm toán.
  - [`core-security-policy/code-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/core-security-policy/code-generation/code-summary.md)
  - [`data-access-tools/code-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/data-access-tools/code-generation/code-summary.md): Tổng kết 16 Typed Tools.
  - [`multi-agent-orchestrator/code-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/multi-agent-orchestrator/code-generation/code-summary.md): Runtime điều phối, router delegation và LLM adapters.
  - [`hybrid-rag-service/code-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/hybrid-rag-service/code-generation/code-summary.md): RAG tiếng Việt lai và lọc Document ACL.
  - [`web-portal-frontend/code-summary.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/web-portal-frontend/code-generation/code-summary.md): Frontend 7 phân hệ.
- **Build, Test & CI Pipeline**:
  - [`build-instructions.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/build-and-test/build-instructions.md): Hướng dẫn cài đặt, cấu hình `.env` và khởi chạy server.
  - [`test-results.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/build-and-test/test-results.md): Kết quả kiểm thử tự động (47/47 passed trong 13.39s).
  - [`ci-config.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/ci-pipeline/ci-config.md): Cấu hình GitHub Actions CI Workflow.
  - [`quality-gates.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/construction/ci-pipeline/quality-gates.md): 5 Tiêu chuẩn kiểm soát chất lượng khi merge code.
- **Verification Gate 3**:
  - [`phase-check-construction.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/verification/phase-check-construction.md): **PASSED**.

---

### 4. Phase 4: Operation (Triển khai, Giám sát & Vận hành Bền vững)
- **Deployment & Resilience**:
  - [`deployment-strategy.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/deployment-pipeline/deployment-strategy.md): Đóng gói Docker container và chiến lược Rolling Update.
  - [`rollback-runbook.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/deployment-pipeline/rollback-runbook.md): Quy trình Rollback khẩn cấp khi gặp sự cố.
- **Observability & SLO**:
  - [`dashboards.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/observability-setup/dashboards.md): Bảng điều khiển giám sát Telemetry và Audit.
  - [`alarms.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/observability-setup/alarms.md): Ngưỡng cảnh báo sự cố bảo mật, mã lỗi 429 và độ trễ.
  - [`slo-config.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/observability-setup/slo-config.md): Cam kết chất lượng dịch vụ (SLO: 99.9% uptime, 0% rò rỉ C3).
- **Incident Response**:
  - [`runbooks.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/incident-response/runbooks.md): Hướng dẫn xử lý lỗi 429, hot-switch model và điều tra rò rỉ dữ liệu.
  - [`escalation-matrix.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/incident-response/escalation-matrix.md): Ma trận phân cấp leo thang sự cố (SEV-1 đến SEV-4).
- **Optimization & Continuous Learning**:
  - [`cost-analysis.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/feedback-optimization/cost-analysis.md): Phân tích hiệu quả chi phí token nhờ Prompt Caching (tiết kiệm ~70%).
  - [`feedback-loop.md`](file:///d:/02_Projects/enterprise-agent-hub/aidlc/operation/feedback-optimization/feedback-loop.md): Vòng lặp cải tiến liên tục từ đánh giá 👍/👎 của người dùng.
