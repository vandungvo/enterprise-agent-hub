# User Personas Specification

## Persona 1: Nhân viên thông thường (Employee)
- **Đại diện tiêu biểu**: `dev.alpha` (Software Engineer L3 tại Studio Alpha), `newbie` (Nhân viên mới).
- **Mục tiêu & Nhu cầu**:
  - Tự tra cứu chính sách công ty, nội quy, bảo mật.
  - Xem phiếu lương của chính mình, hiểu rõ các khoản trừ thuế TNCN và bảo hiểm.
  - Kiểm tra số dư ngày phép, nộp đơn nghỉ phép online.
  - Tra cứu hướng dẫn IT, kết nối VPN, xin cấp quyền.
  - Nộp đề nghị thanh toán công tác phí hoặc chi phí mua sắm thiết bị.
- **Quyền hạn**: Chỉ truy cập dữ liệu cá nhân của chính mình (`self`) và thông tin nội bộ C1 công khai.

## Persona 2: Quản lý trực tiếp (Manager)
- **Đại diện tiêu biểu**: `manager.alpha` (Engineering Manager Studio Alpha).
- **Mục tiêu & Nhu cầu**:
  - Toàn bộ quyền hạn của một nhân viên thông thường.
  - Xem lịch vắng mặt và loại nghỉ phép của các thành viên trực thuộc team.
  - Phê duyệt hoặc từ chối các đơn nghỉ phép, đề nghị thanh toán của cấp dưới.
  - Xem các số liệu tổng hợp nhân sự và quỹ lương của team (tuân thủ k-anonymity k=5).
- **Quyền hạn**: Dữ liệu công việc của tuyến báo cáo trực tiếp (`direct_reports`), không xem được lương cá nhân của cấp dưới.

## Persona 3: Lãnh đạo Khối kinh doanh (BU CEO / Unit Head)
- **Đại diện tiêu biểu**: `head.games` (CEO Sao Mai Games).
- **Mục tiêu & Nhu cầu**:
  - Nắm bắt bức tranh toàn cảnh về nhân sự của khối: Headcount, tỷ lệ tuyển dụng mới, tỷ lệ nghỉ việc (attrition).
  - Giám sát quỹ lương và tiến độ giải ngân ngân sách của khối so với kế hoạch năm.
  - Phê duyệt các khoản chi lớn (> 20 triệu VNĐ) từ các bộ phận bên dưới.
- **Quyền hạn**: Số liệu tổng hợp nhân sự/ngân sách của toàn bộ cây đơn vị (`subtree`), lương cá nhân của cấp dưới trực tiếp.

## Persona 4: CEO Tập đoàn (Group CEO)
- **Đại diện tiêu biểu**: `ceo` (Tổng Giám đốc Tập đoàn Sao Mai).
- **Mục tiêu & Nhu cầu**:
  - Báo cáo chiến lược toàn tập đoàn: So sánh biến động nhân sự, quỹ lương giữa các khối (Games, Pay, Cloud).
  - Tra cứu tài liệu định hướng chiến lược C3 trong KB Lãnh đạo.
  - Xem lương của các Phó TGĐ và CEO khối trực tiếp dưới quyền.
- **Quyền hạn**: Số liệu tổng hợp toàn tập đoàn (k=3), dữ liệu cá nhân của các cấp dưới trực tiếp.

## Persona 5: Chuyên viên C&B & HRBP (People Specialist)
- **Đại diện tiêu biểu**: `cnb` (Chuyên viên C&B Tập đoàn), `hrbp.games` (HRBP Khối Games).
- **Mục tiêu & Nhu cầu**:
  - Tra cứu hồ sơ nhân sự đầy đủ và mức lương cá nhân để phục vụ nghiệp vụ tính lương/bảo hiểm.
  - Phân tích phân bổ thang bảng lương theo cấp bậc (không bị ẩn nhóm nhỏ k=1 đối với C&B).
  - Soạn thảo và cập nhật tài liệu chính sách vào Knowledge Base.
- **Quyền hạn**: Quyền truy cập lương cá nhân theo phạm vi khối hoặc toàn tập đoàn (mọi truy vấn đều bị ghi log kiểm toán bắt buộc).

## Persona 6: Tài chính Kế toán (Finance Specialist & CFO)
- **Đại diện tiêu biểu**: `cfo` (Giám đốc Tài chính), `finance.pay` (Kế toán khối Pay).
- **Mục tiêu & Nhu cầu**:
  - Kiểm soát ngân sách, thẩm tra tính hợp lệ của đề nghị thanh toán.
  - Báo cáo chi phí và ngân sách thực tế so với kế hoạch.
- **Quyền hạn**: Dữ liệu ngân sách và chi phí theo phạm vi phụ trách.

## Persona 7: Quản trị nền tảng (Platform Admin) & Kiểm toán (Auditor)
- **Đại diện tiêu biểu**: `itadmin` (Platform Admin), `auditor` (Internal Auditor).
- **Mục tiêu & Nhu cầu**:
  - Admin: Quản lý cấu hình agent, knowledge base, theo dõi chi phí token, tải lại cấu hình hệ thống.
  - Auditor: Kiểm tra nhật ký truy cập dữ liệu nhạy cảm C3, rà soát các lần người dùng bị từ chối truy cập.
- **Quyền hạn**: Admin quản trị kỹ thuật nhưng KHÔNG được phép đọc dữ liệu nhân sự; Auditor xem toàn bộ nhật ký truy cập.
