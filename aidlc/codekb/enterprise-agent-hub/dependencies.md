# Dependency Inventory & Licenses

## 1. Direct Python Dependencies

| Package Name | Version Spec | License | Purpose in System |
|---|---|---|---|
| `fastapi` | `>=0.115` | MIT | Web framework cung cấp REST endpoints & SSE streaming |
| `uvicorn` | `>=0.34` | BSD-3-Clause | ASGI web server |
| `sqlalchemy` | `>=2.0` | MIT | ORM và database access abstraction |
| `pydantic` | `>=2.10` | MIT | Data parsing, validation, Pydantic typed tools |
| `pyyaml` | `>=6.0` | MIT | Đọc file cấu hình platform.yaml và policies.yaml |
| `anthropic` | `>=2.6.0` | MIT | SDK kết nối Anthropic Messages API và Prompt Caching |
| `httpx` | `>=0.28` | BSD-3-Clause | Async HTTP client gọi Google Gemini API và OpenAI compat |
| `numpy` | `>=2.0` | BSD-3-Clause | Vector math cho RAG vector similarity và BM25 |
| `pypdf` | `>=5.0` | BSD-3-Clause | Trích xuất nội dung văn bản từ tài liệu PDF |
| `python-docx` | `>=1.1` | MIT | Trích xuất văn bản từ tài liệu Microsoft Word |
| `python-multipart`| `>=0.0.20`| Apache-2.0 | Xử lý multipart form data khi upload file |

## 2. Development & Optional Dependencies

| Package Name | Version Spec | Purpose |
|---|---|---|
| `pytest` | `>=8.0` | Automated unit và integration testing |
| `fastembed` | `>=0.4` (optional) | Local dense embedding inference không cần gọi API ngoài |

## 3. External Service Dependencies
- **Anthropic Claude API**: Endpoint chính (`api.anthropic.com`).
- **Google Generative AI API**: Endpoint dự phòng (`generativelanguage.googleapis.com`).
- **Internal HRIS / Core Database**: Cung cấp dữ liệu nhân viên, quan hệ quản lý và vai trò.
- **Enterprise SSO Provider**: OIDC endpoint cho xác thực người dùng tập đoàn.
