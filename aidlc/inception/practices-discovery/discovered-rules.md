# Discovered Invariant Rules

## Rule 1: No Text-to-SQL on Core Data
- **Severity**: CRITICAL
- **Description**: Tuyệt đối không cung cấp công cụ dạng text-to-SQL tự do cho AI model truy cập cơ sở dữ liệu nhân sự và tài chính. Mọi truy vấn phải thông qua các hàm chuyên biệt đã định nghĩa trước có kiểm tra `policy.require()` hoặc `policy.scope()`.

## Rule 2: Per-Request Principal Reconstruction
- **Severity**: CRITICAL
- **Description**: Thông tin danh tính và quyền hạn (`Principal`) không được lưu trữ trong token client hoặc lấy từ tham số request của người dùng. Mỗi request phải tái tạo Principal trực tiếp từ cơ sở dữ liệu HRIS bằng phiên đăng nhập hợp lệ.

## Rule 3: K-Anonymity with Complementary Suppression
- **Severity**: HIGH
- **Description**: Các báo cáo tổng hợp nhân sự và quỹ lương phải kiểm tra ngưỡng số lượng nhân sự `k` (mặc định k=5 cho quản lý/HRBP, k=3 cho CFO/CEO). Nếu chỉ có duy nhất 1 nhóm bị ẩn, bắt buộc phải ẩn bổ sung thêm nhóm nhỏ thứ hai để triệt tiêu nguy cơ suy ngược số liệu qua hiệu số tổng.

## Rule 4: Action Approval Requirement
- **Severity**: HIGH
- **Description**: Bất kỳ công cụ nào tạo ra thay đổi trạng thái trong hệ thống (đơn nghỉ phép, đề nghị thanh toán) phải chuyển vào hàng đợi phê duyệt (`approval_requests`) và được duyệt bởi người quản lý có thẩm quyền theo quan hệ báo cáo, trừ khi có cấu hình `approval_override` rõ ràng (như IT ticket).
