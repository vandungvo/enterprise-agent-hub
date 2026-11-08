# Component Inventory & Tool Registry

## 1. Domain Agents Inventory

| Agent ID | Tên hiển thị | Vai trò | Mô hình & Effort | Danh sách Tools | Knowledge Bases |
|---|---|---|---|---|---|
| `router` | Trợ lý Sao Mai | Router / Dispatcher | claude-opus-5-5 (low) | `delegate_to_agent` | Không |
| `people` | Trợ lý Nhân sự & Phúc lợi | Specialist | claude-opus-5-5 (medium) | `search_knowledge`, `get_employee_profile`, `get_payslip`, `get_compensation_history`, `get_leave_balance`, `list_leave_requests`, `submit_leave_request`, `team_calendar`, `directory_search`, `get_current_time` | `people_policy`, `company`, `leadership` |
| `insights` | Trợ lý Phân tích Lãnh đạo | Specialist | claude-opus-5-5 (high) | `workforce_analytics`, `budget_report`, `get_org_chart`, `directory_search`, `search_knowledge`, `get_current_time` | `leadership`, `people_policy`, `company` |
| `finance` | Trợ lý Tài chính | Specialist | claude-opus-5-5 (medium) | `search_knowledge`, `submit_expense_claim`, `list_expense_claims`, `budget_report`, `get_current_time` | `finance_policy`, `company` |
| `it_helpdesk`| IT Helpdesk | Specialist | claude-opus-5-5 (medium) | `search_knowledge`, `create_ticket`, `get_current_time` | `it_kb`, `company` |
| `company_info`| Thông tin tập đoàn & Danh bạ| Specialist | claude-opus-5-5 (low) | `search_knowledge`, `directory_search`, `get_org_chart`, `get_current_time` | `company` |

## 2. Typed Pydantic Tools Inventory (16 Tools)

| Tool Name | Module | Phân loại dữ liệu | Kiểm tra Policy | Mô tả chức năng |
|---|---|---|---|---|
| `directory_search` | `tools/people.py` | C1 Nội bộ | Không | Tìm kiếm đồng nghiệp theo tên, đơn vị, email |
| `get_org_chart` | `tools/people.py` | C1 Nội bộ | Không | Lấy sơ đồ cây tổ chức và người đứng đầu |
| `get_employee_profile` | `tools/people.py` | C2 Mật / C3 Tuyệt mật | `profile.employment`, `profile.personal` | Xem hồ sơ nhân viên (ẩn thông tin cá nhân nếu không có quyền) |
| `get_payslip` | `tools/people.py` | C3 Tuyệt mật | `compensation.individual` | Xem chi tiết phiếu lương một hoặc nhiều kỳ |
| `get_compensation_history` | `tools/people.py` | C3 Tuyệt mật | `compensation.individual` | Xem lịch sử điều chỉnh lương qua các năm |
| `get_leave_balance` | `tools/people.py` | C2 Mật | `leave.individual` | Xem số dư phép năm, phép tồn, ngày nghỉ ốm |
| `list_leave_requests` | `tools/people.py` | C2 Mật | `leave.individual` | Danh sách các đơn nghỉ phép đã nộp |
| `team_calendar` | `tools/people.py` | C1 / C2 | `leave.calendar` | Lịch vắng mặt của team (ẩn loại nghỉ đối với đồng nghiệp) |
| `submit_leave_request` | `tools/people.py` | C2 Mật | Action (HITL) | Nộp đơn nghỉ phép vào hàng đợi phê duyệt của quản lý |
| `workforce_analytics` | `tools/analytics.py` | C2 Mật | `workforce.aggregate`, `compensation.aggregate` | Phân tích headcount, tuyển mới, nghỉ việc, quỹ lương (k-anonymity) |
| `budget_report` | `tools/analytics.py` | C2 Mật | `finance.budget` | Báo cáo ngân sách kế hoạch vs thực tế theo đơn vị |
| `submit_expense_claim` | `tools/workflow.py` | C2 Mật | Action (HITL) | Nộp đề nghị thanh toán/công tác phí (>20tr chuyển trưởng khối) |
| `list_expense_claims` | `tools/workflow.py` | C2 Mật | `expense.individual` | Danh sách đề nghị thanh toán của bản thân hoặc đơn vị |
| `create_ticket` | `tools/workflow.py` | C1 Nội bộ | Action (Direct) | Tạo ticket IT hỗ trợ (bỏ qua hàng đợi duyệt) |
| `search_knowledge` | `tools/knowledge.py`| C1 / C2 / C3 | Document ACL | Tìm kiếm tri thức lai BM25 + Vector trong KB được phép |
| `get_current_time` | `tools/builtin.py` | C0 Công khai | Không | Lấy ngày giờ hiện tại theo múi giờ hệ thống |
