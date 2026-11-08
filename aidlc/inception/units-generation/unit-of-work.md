# Units of Work Specification

## Unit Decomposition Matrix

| Unit ID | Name | Kind | Primary Package / Files | Description & Responsibilities |
|---|---|---|---|---|
| **U-01** | `core-security-policy` | `service` | `app/access/policy.py`, `app/access/auth.py`, `config/policies.yaml` | ABAC Policy Engine, thẩm định quyền truy cập dữ liệu, dựng Principal từ HRIS mỗi request, thuật toán k-anonymity & complementary suppression, che mờ log dữ liệu C3, ghi log kiểm toán. |
| **U-02** | `data-access-tools` | `library` | `app/tools/people.py`, `app/tools/analytics.py`, `app/tools/workflow.py`, `app/tools/builtin.py` | Bộ công cụ 16 Typed Pydantic Tools cho HR, Lương, Phép, Báo cáo nhân sự, Ngân sách, Đề nghị chi phí, Ticket IT. |
| **U-03** | `multi-agent-orchestrator` | `service` | `app/agents/runtime.py`, `app/agents/conversation.py`, `app/agents/registry.py`, `app/llm/base.py` | Multi-Agent Runtime, Router delegation, điều phối vòng lặp tool execution, streaming Server-Sent Events (SSE), adapters đa nhà cung cấp LLM (Claude, Gemini, OpenAI). |
| **U-04** | `hybrid-rag-service` | `service` | `app/rag/service.py`, `app/rag/parsing.py`, `app/rag/text.py` | RAG lai tiếng Việt: Tokenizer BM25 có/không dấu, Vector embeddings, Reciprocal Rank Fusion (RRF), trích xuất tài liệu đa định dạng (.pdf, .docx, .csv), Document ACL filtering. |
| **U-05** | `web-portal-frontend` | `ui` | `static/index.html`, `static/app.js`, `static/styles.css` | Giao diện Web Portal người dùng: 7 phân hệ (Chat, Phê duyệt HITL, Quyền của tôi, Tra cứu KB, Đo lường AI, Kiểm toán, Quản trị). |
