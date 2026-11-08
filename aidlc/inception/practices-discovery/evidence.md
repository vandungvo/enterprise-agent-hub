# Discovered Rules Evidence

| Rule ID | File Path | Code Evidence / Line Anchor |
|---|---|---|
| Rule 1 (No Text-to-SQL) | `app/tools/people.py`, `app/tools/analytics.py` | Toàn bộ các tool đều sử dụng SQLAlchemy select có schema cố định và tham số gõ kiểu chặt chẽ |
| Rule 2 (Principal Reconstruction) | `app/access/auth.py` | Hàm `get_current_principal()` thực thi truy vấn trực tiếp bảng `employees`, `org_units`, `role_assignments` ở mỗi request |
| Rule 3 (K-Anonymity & Suppression) | `app/tools/analytics.py` | Logic kiểm tra `len(group) < k` và cơ chế `suppress_secondary` khi chỉ có 1 nhóm vi phạm |
| Rule 4 (Action Approval) | `app/tools/workflow.py`, `app/tools/people.py` | Kiểm tra trạng thái và tạo bản ghi `approval_requests` với `approver_id = principal.manager_id` |
