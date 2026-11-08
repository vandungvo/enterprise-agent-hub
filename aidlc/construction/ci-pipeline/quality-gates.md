# Quality Gates & Merge Invariants

| Gate ID | Tiêu chuẩn | Ngưỡng | Cơ chế kiểm tra | Trạng thái |
|---|---|---|---|---|
| **QG-01** | Unit test pass rate | 100% trên SQLite **và** PostgreSQL, Python 3.12 + 3.13 | Job `test` trong CI | ✅ Enforced |
| **QG-02** | Policy regression | 100% test ABAC / k-anonymity / ACL tài liệu | `tests/test_policy.py` (nằm trong QG-01) | ✅ Enforced |
| **QG-03** | Lint sạch | `ruff check .` không lỗi | Job `lint` trong CI | ✅ Enforced |
| **QG-04** | Schema khớp migration | `alembic revision --autogenerate` không sinh thay đổi | `tests/test_migrations.py::test_migrations_match_models` | ✅ Enforced |
| **QG-05** | Hardening không hồi quy | Request id, security headers, login throttling, cron auth, không lộ lỗi nội bộ | `tests/test_hardening.py` | ✅ Enforced |
| **QG-09** | Kiến trúc phân lớp | Không module nào import ngược chiều phụ thuộc; không import tương đối | `tests/test_architecture.py` | ✅ Enforced |
| **QG-06** | Thời gian chạy suite | < 30 giây (LLM giả lập `fake_claude.py`) | Thời lượng job CI | ✅ Theo dõi (hiện ~13–16s) |
| **QG-07** | Không lộ secret | Không có API key / mật khẩu thật trong repo | Gitleaks / GitHub secret scanning | 🔜 Planned (chưa có trong workflow) |
| **QG-08** | Không Text-to-SQL | Tool không dựng SQL từ input người dùng | Review: SQL chỉ dùng tham số đặt tên; tên cột động chỉ từ whitelist cố định | 🔜 Planned (chưa có kiểm tra tự động) |

Merge vào `main` chỉ khi QG-01 → QG-05 và QG-09 xanh. Bật branch protection trên GitHub (Settings → Branches → Require status checks: `lint`, `test`) để cưỡng chế.
