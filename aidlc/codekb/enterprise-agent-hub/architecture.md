# System Architecture

## 1. High-Level Architecture Overview
Enterprise Agent Hub được thiết kế theo kiến trúc phân lớp hướng dịch vụ (Layered Service-Oriented Architecture) kết hợp mô hình điều phối Multi-Agent hướng sự kiện (Event-driven Multi-Agent Orchestration):

```
+-------------------------------------------------------------------------------+
|                           CLIENT TIER (HTML/JS Web UI)                        |
|   Chat SSE Stream | Approvals | My Permissions | KB Search | Telemetry / Admin|
+---------------------------------------+---------------------------------------+
                                        | HTTP REST / Server-Sent Events (SSE)
+---------------------------------------v---------------------------------------+
|                       APPLICATION TIER (FastAPI Backend)                      |
|                                                                               |
|  [Authentication & Session]        [Principal Builder]                        |
|  - Cookie Session                  - HRIS-backed identity reconstruction      |
|  - Role / Unit / Level resolution  - Manager chain calculation                |
|                                                                               |
|  [Agent Runtime & Orchestration]   [Knowledge & Hybrid RAG]                   |
|  - Router Agent (Intent analysis)  - BM25 Lexical + FastEmbed Vector          |
|  - Specialized Agents (5 domains)  - Reciprocal Rank Fusion (RRF)             |
|  - Pydantic Typed Tools (16 tools) - Document ACL Filtering (roles/units/min) |
|  - Multi-LLM Protocol Adapter      - Tool Definition Registry                 |
|                                                                               |
|  [Governance & Human-in-the-Loop]                                             |
|  - Approval Queue for mutating actions (Leave, Expense, Ticket)               |
|  - Reporting-line auto-routing                                                |
+---------------------------------------+---------------------------------------+
                                        | Deterministic Interception
+---------------------------------------v---------------------------------------+
|                    DATA ACCESS & SECURITY POLICY TIER (ABAC)                  |
|                                                                               |
|  [Policy Engine: app/policy.py + config/policies.yaml]                        |
|  - policy.require() for individual resource checks                            |
|  - policy.scope() for listing and aggregation filtering                       |
|  - K-Anonymity Guard (k=3, k=5) with Complementary Suppression                |
|  - Log Masking & Redaction for C3 fields                                      |
|  - Data Access Audit Logger (data_access_log table)                           |
+---------------------------------------+---------------------------------------+
                                        | SQLAlchemy ORM
+---------------------------------------v---------------------------------------+
|                           DATA PERSISTENCE TIER                               |
|  SQLite (Development & Demo) -> PostgreSQL + RLS (Production Target)          |
|  - HRIS: employees, org_units, role_assignments, payslips, leaves             |
|  - Operations: expense_claims, it_tickets, approval_requests                  |
|  - System: conversations, messages, data_access_log, feedback                 |
|  - RAG Index: documents, chunks, bm25_index, vector_embeddings                |
+-------------------------------------------------------------------------------+
```

## 2. Nine Layers of Defense (Defense-in-depth)
1. **Agent Access Filtering**: Router agent chỉ nhìn thấy các agent mà người dùng có quyền truy cập (theo khai báo `access.roles` trong `platform.yaml`).
2. **Tool Scoping by Agent**: Mỗi agent chỉ được phép gọi danh sách tool được cấu hình cụ thể cho nó.
3. **Data-Tier Policy Verification**: Mọi tool đọc dữ liệu đều gọi `policy.require()` hoặc `policy.scope()` trước khi thực thi truy vấn SQL.
4. **Document-Level ACL**: Chunk của tài liệu chỉ được tìm kiếm và trả về nếu Principal thỏa mãn `roles`, `units`, và `min_level`.
5. **K-Anonymity & Complementary Suppression**: Số liệu tổng hợp tự động ẩn các nhóm dưới ngưỡng `k`, và ẩn thêm nhóm nhỏ thứ hai nếu chỉ có 1 nhóm bị ẩn để ngăn phép tính hiệu số.
6. **Operational Log Redaction**: Kết quả trả về của các tool C3 bị che mờ trong log hệ thống mà Platform Admin có thể xem.
7. **Comprehensive Audit Trail**: Mọi truy cập vào dữ liệu C3 của người khác và mọi lần truy cập bị từ chối đều được ghi vào bảng `data_access_log`.
8. **Sensitive Conversation Retention**: Các phiên chat chạm dữ liệu C3 tự động bị xóa sau 30 ngày.
9. **Impact Action Gates (HITL)**: Hành động thay đổi trạng thái luôn yêu cầu phê duyệt từ cấp quản lý trực tiếp hoặc cấp có thẩm quyền.
