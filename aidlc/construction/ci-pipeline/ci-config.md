# Continuous Integration Pipeline Specification

> Nguồn sự thật: [`.github/workflows/ci.yml`](../../../.github/workflows/ci.yml). Tài liệu này giải thích workflow, không sao chép nó.

## Jobs

| Job | Chạy gì | Mục đích |
|---|---|---|
| `lint` | `ruff check .` (cấu hình trong `pyproject.toml`) | Lỗi cú pháp, import thừa/sai thứ tự, bugbear, pyupgrade |
| `test` (ma trận 4 ô) | `pytest` với Python **3.12** (runtime Vercel) và **3.13**, trên **SQLite** và **PostgreSQL 16** (service container) | Mọi bất biến phân quyền + code dialect-neutral chạy đúng trên cả hai database |

- Kích hoạt: push lên `main` và mọi pull request; `concurrency` hủy lần chạy cũ của cùng nhánh.
- Cài đặt: `pip install -r requirements-dev.txt` (runtime đã pin + `pytest`, `ruff` pin cố định).
- PostgreSQL: biến `TEST_DATABASE_URL` trỏ vào service container; `tests/conftest.py` xóa schema rồi chạy **Alembic migrations** như lúc khởi động production, nên migration được kiểm thử ở mỗi lần CI.

## Chạy tương đương ở local

```powershell
.\.venv\Scripts\pip install -r requirements-dev.txt
.\.venv\Scripts\ruff check .
.\.venv\Scripts\python -m pytest                                   # SQLite
$env:TEST_DATABASE_URL="postgresql://postgres@localhost:5432/agenthub_test"
.\.venv\Scripts\python -m pytest                                   # PostgreSQL
```

## Deploy

CI không deploy. Production trên Vercel deploy bằng `vercel --prod` (hoặc nối repo GitHub với project để Vercel tự deploy khi `main` xanh). Xem [`deployment-strategy.md`](../../operation/deployment-pipeline/deployment-strategy.md).
