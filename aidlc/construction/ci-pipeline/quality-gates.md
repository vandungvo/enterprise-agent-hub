# Quality Gates & Merge Invariants

## CI Quality Gate Rules

| Gate ID | Tên tiêu chuẩn | Ngưỡng bắt buộc (Threshold) | Cơ chế kiểm tra |
|---|---|---|---|
| **QG-01** | **Unit Test Pass Rate** | 100% Passed (0 thất bại) | `pytest tests/` |
| **QG-02** | **Policy Regression Invariant** | 100% Passed trên mọi rule ABAC và K-anonymity | `pytest tests/test_policy.py` |
| **QG-03** | **Security Leak Check** | Không lộ credentials, API keys hoặc raw secret trong code | Gitleaks / Pattern scanner |
| **QG-04** | **No Text-to-SQL Check** | 0 câu lệnh Text-to-SQL trong toàn bộ module `app/tools/` | Static AST analysis |
| **QG-05** | **Test Execution Time** | Toàn bộ suite chạy dưới 30 giây (nhờ `fake_claude.py`) | CI duration monitor |
