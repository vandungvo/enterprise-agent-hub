# Code Structure & Directory Organization

## 1. Directory Tree & Module Responsibilities

```
enterprise-agent-hub/
├── app/                        # Mã nguồn ứng dụng (import tuyệt đối; chiều phụ thuộc kiểm tra bởi tests/test_architecture.py)
│   ├── main.py                 # create_app(): logging, validate cấu hình, middleware, router, UI tĩnh
│   ├── bootstrap.py            # Khởi động: migrate + seed demo + purge, trong seed_lock (pg_advisory_lock)
│   ├── models.py               # Model ORM nền tảng (users, conversations, chunks, llm_calls, pending_actions...)
│   ├── core/                   # Hạ tầng: settings (env, validate), db (engine, session, lock), migrations (Alembic), observability
│   ├── access/                 # principal.py (Principal từ HRIS), policy.py (ABAC PDP, audit), auth.py (token HMAC, throttle, deps)
│   ├── hris/                   # schema, queries, org (cache TTL), payroll (thuế/bảo hiểm), demo_data (Sao Mai Group)
│   ├── llm/                    # client (chọn provider), pricing, base (stream/retry), gemini, openai_compat
│   ├── agents/                 # registry (platform.yaml), runtime (tool-use loop, delegation, HITL), conversation (chat_turn, retention)
│   ├── api/                    # Router theo domain: identity, chat, knowledge, approvals, audit, metrics, admin, health, internal
│   │
│   ├── rag/                    # Hệ thống RAG tiếng Việt lai (BM25 + Dense Vectors)
│   │   ├── service.py          # Dịch vụ tìm kiếm tài liệu, BM25 indexing, vector search, RRF fusion
│   │   ├── parsing.py          # Trích xuất văn bản từ file .pdf, .docx, .md, .txt, .csv
│   │   └── text.py             # Tokenizer tiếng Việt hiểu có dấu và không dấu, BM25 math
│   │
│   └── tools/                  # 16 công cụ nghiệp vụ gõ kiểu chặt chẽ (Pydantic models)
│       ├── base.py             # Lớp cơ sở Tool, metadata, schema definition
│       ├── people.py           # Công cụ nhân sự: hồ sơ, lương, số dư phép, nộp đơn nghỉ
│       ├── analytics.py        # Công cụ phân tích: headcount, biến động nhân sự, quỹ lương, k-anonymity
│       ├── workflow.py         # Công cụ quy trình: đề nghị chi phí, tạo ticket IT
│       └── knowledge.py        # Công cụ tra cứu tri thức: search_knowledge
│
├── config/                     # Cấu hình hệ thống (YAML declarative)
│   ├── platform.yaml           # Khai báo agents, prompts, effort, knowledge bases, quyền truy cập agent
│   └── policies.yaml           # Ma trận chính sách ABAC trên từng resource và vai trò
│
├── static/                     # Giao diện người dùng Web thuần (Zero-build HTML/JS/CSS)
│   ├── index.html              # Trang chủ ứng dụng, bố cục 7 phân hệ
│   ├── app.js                  # Logic client-side, kết nối SSE, xử lý trace và render markdown
│   └── styles.css              # Giao diện responsive, dark/light theme
│
├── seed_docs/                  # Tài liệu mẫu ban đầu nạp vào 5 Knowledge Base (kèm metadata ACL)
├── aidlc/                      # Bộ tài liệu AI-DLC (gồm cả use-case catalog, permission model, BA guide)
├── tests/                      # 114 test pytest (gồm 51 test kiến trúc) (SQLite hoặc TEST_DATABASE_URL PostgreSQL), gồm migrations và hardening
├── migrations/                 # Alembic: env.py + versions/ (0001 baseline, 0002 scalability)
├── .github/workflows/ci.yml    # CI: ruff + pytest trên SQLite/PostgreSQL × Python 3.12/3.13
├── Dockerfile, docker-compose.yml # Image production (non-root, healthcheck) + stack app + PostgreSQL
├── pyproject.toml              # Dependency runtime (nguồn chính) + ruff, pytest; requirements*.txt là bản sao cho pip/Docker
├── api/index.py                # Entrypoint Vercel Serverless Function (re-export app.main:app)
├── vercel.json                 # Cấu hình Vercel: rewrite mọi route về FastAPI, includeFiles
└── requirements.txt            # Danh mục thư viện phụ thuộc Python
```

## 2. Key Abstractions & Design Patterns
- **Principal Pattern**: Thực thể đại diện người dùng được nạp động từ HRIS mỗi request, mang đầy đủ thông tin vị trí tổ chức, cây quản lý và danh sách vai trò gán.
- **Adapter Pattern**: `GeminiClient` và `OpenAICompatClient` bọc các API khác nhau để trả về cùng định dạng `BetaMessage` và tool-call stream của Anthropic Messages API.
- **Policy Enforcement Point (PEP) & Policy Decision Point (PDP)**: Tập trung toàn bộ logic quyết định tại `app/access/policy.py`, các tool đóng vai trò là PEP bắt buộc phải gọi PDP.
- **Hybrid Retrieval Pattern**: Kết hợp Lexical Search (BM25) với Dense Vector Search qua thuật toán Reciprocal Rank Fusion (RRF).
