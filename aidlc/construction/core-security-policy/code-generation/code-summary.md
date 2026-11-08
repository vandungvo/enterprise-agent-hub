# Code Generation Summary: Core Security Policy (U-01)

## 1. Implemented Files
- **`app/access/policy.py`**:
  - `PolicyEngine`: Lớp quản lý chính sách nạp từ YAML.
  - `require_access()`: Hàm kiểm tra quyền trên một bản ghi cá nhân.
  - `get_data_scope()`: Hàm xác định phạm vi truy vấn cho danh sách/tổng hợp.
  - `log_sensitive_access()`: Hàm ghi log vào bảng `data_access_log`.
- **`app/access/auth.py`**:
  - `create_session()` / `principal_from_token()`: phát hành và xác thực token stateless ký HMAC-SHA256 (email + hạn dùng), sau đó dựng lại `Principal` từ HRIS (ADR-06).
  - `current_principal()`: FastAPI dependency đọc header `Authorization: Bearer`, trả 401 nếu token sai/hết hạn; `require_any_role()` chặn endpoint theo vai trò.
- **`config/policies.yaml`**:
  - Khai báo declarative ma trận phân quyền cho 10 resources.

## 2. Unit & Regression Tests
- **`tests/test_policy.py`**:
  - `test_self_access_compensation()`: Kiểm tra nhân viên tự xem lương chính mình -> HỢP LỆ.
  - `test_cross_employee_access_denied()`: Nhân viên xem lương đồng nghiệp -> BỊ TỪ CHỐI.
  - `test_manager_access_scope()`: Quản lý xem lịch nghỉ của team -> HỢP LỆ.
  - `test_k_anonymity_suppression()`: Kiểm tra ẩn nhóm nhỏ và complementary suppression.
