# Functional Specification: Core Security Policy (U-01)

## 1. Domain Entities & Data Models
- **`Principal`**:
  - `employee_id`: Mã nhân viên (e.g. `EMP001`).
  - `email`: Địa chỉ thư điện tử công vụ.
  - `unit_id`: Đơn vị trực thuộc hiện tại.
  - `unit_path`: Chuỗi đường dẫn phân cấp đơn vị (`SMG-GROUP/SMG/STUDIO-ALPHA`).
  - `manager_id`: Mã quản lý trực tiếp.
  - `level`: Cấp bậc chuyên môn (L1 - L8).
  - `roles`: Tập hợp các vai trò tự động (`employee`, `manager`, `unit_head`) và vai trò được gán (`ceo`, `exec`, `chro`, `cfo`, `cnb`, `hrbp`, `finance`, `auditor`, `it_support`, `platform_admin`).
  - `role_scopes`: Bản đồ phạm vi tương ứng của từng vai trò (e.g. `hrbp: SMG`).

## 2. Policy Enforcement Engine Logic (`app/access/policy.py`)
Mỗi yêu cầu truy cập dữ liệu được thẩm định bằng quy tắc:
1. **`policy.require(principal, resource, target_id)`**:
   - Tra cứu cấu hình `policies[resource]`.
   - Nếu `target_id == principal.employee_id` và rule cho phép `self`: **GRANT**.
   - Nếu `target_id in principal.direct_reports` và rule cho phép `direct_reports`: **GRANT**.
   - Nếu `target_id in principal.subtree` và rule cho phép `subtree`: **GRANT**.
   - Nếu `principal` có vai trò khớp với `role_scope` và đơn vị của `target_id` nằm trong scope: **GRANT**.
   - Không khớp bất kỳ quy tắc nào: **DENY** và ghi log vào `data_access_log`.

2. **`policy.scope(principal, resource)`**:
   - Trả về danh sách `unit_ids` được phép xem và ngưỡng ẩn danh `k`.
   - Đối với báo cáo tổng hợp: Lãnh đạo cấp cao (CEO, CFO) k=3; Quản lý và HRBP k=5; C&B k=1.

## 3. K-Anonymity & Complementary Suppression Algorithm
- Nếu số lượng bản ghi trong một nhóm < `k`: Ẩn nhóm này (thay thế bằng `[SUPPRESSED: < k employees]`).
- **Complementary Suppression**: Nếu sau bước trên, chỉ có DUY NHẤT 1 nhóm bị ẩn trong khi tổng số của toàn bộ các nhóm được biết: Bắt buộc tìm nhóm nhỏ thứ hai (có số lượng >= k) và ẩn luôn nhóm này để ngăn chặn phép trừ đại số suy ngược con số của nhóm nhỏ.
