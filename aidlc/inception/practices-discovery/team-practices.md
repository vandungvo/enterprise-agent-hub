# Discovered Team Practices

## 1. Development & Architecture Practices
- **Explicit Schemas Over Raw Dicts**: 100% các công cụ gọi hàm của AI agent phải kế thừa từ `BaseTool` và sử dụng Pydantic v2 `BaseModel` để định nghĩa tham số đầu vào và kết quả đầu ra.
- **Declarative Configuration**: Tách rời hoàn toàn định nghĩa Agent, prompts, effort và quyền truy cập agent vào file `config/platform.yaml`. Hệ thống hỗ trợ nạp lại cấu hình nóng (hot reload) mà không cần khởi động lại tiến trình.
- **Deterministic Security over Prompt Engineering**: Không bao giờ ủy thác việc phân quyền cho system prompt của LLM. Mọi kiểm tra quyền truy cập dữ liệu được thực thi bằng mã Python xác định trong `app/policy.py`.

## 2. Testing Practices
- **Deterministic Fast Test Suite**: 100% các bài test trong `tests/` sử dụng `fake_claude.py` hoặc mock objects để đảm bảo thời gian chạy dưới 15 giây, kiểm thử độc lập không phụ thuộc vào kết nối mạng internet hay chi phí token LLM thực tế.
- **Policy Exhaustive Coverage**: Mọi resource và mọi cấp độ phân quyền (`self`, `direct_reports`, `subtree`, `same_unit`, `role_scope`) đều có test case kiểm thử cả trường hợp cho phép và trường hợp bị từ chối trong `tests/test_policy.py`.

## 3. Operational & Privacy Practices
- **Data Minimization & Redaction**: Kết quả trả về của các công cụ tra cứu lương (`get_payslip`, `get_compensation_history`) tự động bị loại bỏ khỏi operational log của hệ thống (`REDACTED_TOOL_OUTPUTS`).
- **Audit Logging**: Ghi nhận toàn bộ các lần truy cập dữ liệu C3 và các lần từ chối truy cập vào bảng `data_access_log` để phục vụ thanh tra.
