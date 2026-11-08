# Code Generation Summary: Data Access Tools (U-02)

## 1. Implemented Tools Inventory
- **`app/tools/people.py`**:
  - `get_employee_profile`: Trả về hồ sơ công việc hoặc thông tin cá nhân tùy theo quyền `profile.personal`.
  - `get_payslip`: Truy xuất phiếu lương chi tiết với kiểm tra bắt buộc `compensation.individual`.
  - `get_compensation_history`: Lịch sử biến động lương qua các năm.
  - `get_leave_balance`: Số dư ngày phép và nghỉ ốm.
  - `list_leave_requests`: Danh sách các đơn nghỉ phép.
  - `team_calendar`: Lịch vắng mặt nhóm (tự động lọc bỏ cột loại nghỉ đối với đồng nghiệp).
  - `submit_leave_request`: Tạo yêu cầu phê duyệt nghỉ phép chuyển đến quản lý trực tiếp.
  - `directory_search`: Tra cứu danh bạ nội bộ công khai.
- **`app/tools/analytics.py`**:
  - `workforce_analytics`: Báo cáo biến động nhân sự và quỹ lương có áp dụng k-anonymity.
  - `budget_report`: Báo cáo kế hoạch và thực tế giải ngân ngân sách theo đơn vị.
- **`app/tools/workflow.py`**:
  - `submit_expense_claim`: Nộp đề nghị thanh toán (định tuyến quản lý hoặc trưởng khối nếu > 20tr).
  - `list_expense_claims`: Danh sách đề nghị thanh toán.
  - `create_ticket`: Tạo yêu cầu hỗ trợ IT.

## 2. Security Invariants Preserved
Mọi tool trước khi thực thi truy vấn đều gọi:
```python
policy.require(principal, "resource.name", target_id)
# hoặc
scope = policy.scope(principal, "resource.name")
```
Không có bất kỳ câu lệnh SQL raw hay text-to-SQL nào được phép tồn tại.
