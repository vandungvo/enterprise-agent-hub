# Code Generation Summary: Core Security Policy (U-01)

## 1. Implemented Files
- **`app/policy.py`**:
  - `PolicyEngine`: Lớp quản lý chính sách nạp từ YAML.
  - `require_access()`: Hàm kiểm tra quyền trên một bản ghi cá nhân.
  - `get_data_scope()`: Hàm xác định phạm vi truy vấn cho danh sách/tổng hợp.
  - `log_sensitive_access()`: Hàm ghi log vào bảng `data_access_log`.
- **`app/auth.py`**:
  - `get_current_principal()`: Middleware trích xuất cookie session và query HRIS dựng đối tượng `Principal`.
- **`config/policies.yaml`**:
  - Khai báo declarative ma trận phân quyền cho 10 resources.

## 2. Unit & Regression Tests
- **`tests/test_policy.py`**:
  - `test_self_access_compensation()`: Kiểm tra nhân viên tự xem lương chính mình -> HỢP LỆ.
  - `test_cross_employee_access_denied()`: Nhân viên xem lương đồng nghiệp -> BỊ TỪ CHỐI.
  - `test_manager_access_scope()`: Quản lý xem lịch nghỉ của team -> HỢP LỆ.
  - `test_k_anonymity_suppression()`: Kiểm tra ẩn nhóm nhỏ và complementary suppression.
