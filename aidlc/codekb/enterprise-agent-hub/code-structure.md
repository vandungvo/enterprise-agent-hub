# Code Structure & Directory Organization

## 1. Directory Tree & Module Responsibilities

```
enterprise-agent-hub/
├── app/                        # Mã nguồn ứng dụng chính (Backend)
│   ├── main.py                 # FastAPI app: endpoints HTTP REST, SSE streaming, middleware auth
│   ├── auth.py                 # Xác thực session, trích xuất Principal từ HRIS database
│   ├── chat.py                 # Dịch vụ hội thoại, streaming SSE, xử lý trace agent
│   ├── orchestrator.py         # Multi-agent runtime, dispatch tool, loop gọi hàm với LLM
│   ├── policy.py               # ABAC Policy Engine, kiểm tra quyền require/scope, log audit
│   ├── registry.py             # Quản lý cấu hình agents, knowledge bases từ platform.yaml
│   ├── providers.py            # Nhà cung cấp LLM, lựa chọn adapter (Claude, Gemini, OpenAI)
│   ├── gemini.py               # Adapter chuyển đổi định dạng Gemini sang Messages API
│   ├── openai_compat.py        # Adapter chuyển đổi định dạng OpenAI sang Messages API
│   ├── hris.py                 # Tương tác dữ liệu nhân sự: nhân viên, quan hệ quản lý, chức danh
│   ├── db.py                   # Cấu hình SQLAlchemy, quản lý session và migrations SQLite
│   ├── seed.py                 # Dữ liệu mẫu tập đoàn Sao Mai Group (100 nhân sự, bảng lương, phép)
│   ├── settings.py             # Quản lý biến môi trường Pydantic BaseSettings
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
├── docs/                       # Tài liệu hướng dẫn nghiệp vụ và kỹ thuật hiện hữu
├── tests/                      # Bộ kiểm thử tự động pytest (47 test cases)
└── requirements.txt            # Danh mục thư viện phụ thuộc Python
```

## 2. Key Abstractions & Design Patterns
- **Principal Pattern**: Thực thể đại diện người dùng được nạp động từ HRIS mỗi request, mang đầy đủ thông tin vị trí tổ chức, cây quản lý và danh sách vai trò gán.
- **Adapter Pattern**: `GeminiClient` và `OpenAICompatClient` bọc các API khác nhau để trả về cùng định dạng `BetaMessage` và tool-call stream của Anthropic Messages API.
- **Policy Enforcement Point (PEP) & Policy Decision Point (PDP)**: Tập trung toàn bộ logic quyết định tại `app/policy.py`, các tool đóng vai trò là PEP bắt buộc phải gọi PDP.
- **Hybrid Retrieval Pattern**: Kết hợp Lexical Search (BM25) với Dense Vector Search qua thuật toán Reciprocal Rank Fusion (RRF).
