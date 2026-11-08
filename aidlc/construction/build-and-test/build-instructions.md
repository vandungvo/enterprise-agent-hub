# Build & Installation Instructions

## 1. Prerequisites
- Python 3.11 hoặc mới hơn.
- Trình quản lý gói `pip` hoặc `uv`.
- Hệ điều hành: Linux, macOS hoặc Windows PowerShell.

## 2. Environment Setup & Dependency Installation

```bash
# 1. Tạo môi trường ảo
python -m venv .venv

# 2. Kích hoạt môi trường ảo
# Trên Linux/macOS:
source .venv/bin/activate
# Trên Windows PowerShell:
.venv\Scripts\Activate.ps1

# 3. Cài đặt các thư viện phụ thuộc
pip install -r requirements.txt
```

## 3. Configuration & Environment Variables
Tạo file `.env` từ file mẫu `.env.example`:

```bash
cp .env.example .env
```

Các biến môi trường cốt lõi:
- `ANTHROPIC_API_KEY`: Khóa API của Anthropic Claude (Primary model).
- `GEMINI_API_KEY`: Khóa API Google Gemini (Tùy chọn nếu dùng provider gemini).
- `LLM_PROVIDER`: `claude` (mặc định), `gemini`, hoặc `openai_compat`.
- `DATABASE_URL`: Đường dẫn CSDL SQLite (mặc định `sqlite:///data/enterprise.db`).
- `SENSITIVE_RETENTION_DAYS`: Số ngày lưu trữ các phiên hội thoại C3 (mặc định 30).

## 4. Database Seeding & Startup

```bash
# Khởi tạo dữ liệu mẫu tập đoàn Sao Mai Group (100 nhân viên, lương, phép)
python -m app.seed

# Khởi chạy server FastAPI ở chế độ development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Truy cập giao diện Web tại: `http://localhost:8000`
