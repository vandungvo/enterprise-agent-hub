# Intent Statement

## Problem Statement
Doanh nghiệp dạng tập đoàn với nhiều đơn vị kinh doanh (BU) và phòng ban chức năng đang gặp tình trạng phân mảnh thông tin nghiêm trọng, khiến nhân viên mất nhiều thời gian tra cứu và gửi yêu cầu hành chính (HR, IT, Tài chính, Phúc lợi) qua nhiều kênh rời rạc [Q1]. Đồng thời, các giải pháp chatbot AI thông thường có nguy cơ rò rỉ dữ liệu mật (phiếu lương, quỹ lương, hồ sơ nhân sự, chiến lược kinh doanh) nếu chỉ dựa vào prompt engineering để kiểm soát truy cập [Q1]. Cần một nền tảng trợ lý AI hội thoại thống nhất nhưng phân quyền chặt chẽ ở tầng dữ liệu (ABAC) [Q1].

## Target Customer & Personas
Giải pháp phục vụ toàn thể cán bộ nhân viên và các cấp lãnh đạo trong tập đoàn [Q2]:
- **Nhân viên thông thường**: Tự phục vụ tra cứu chính sách, xem phiếu lương của chính mình, số dư ngày phép, hướng dẫn IT, nộp đơn nghỉ phép và đề nghị thanh toán [Q2].
- **Quản lý trực tiếp (Manager)**: Tra cứu thông tin công việc cấp dưới, xem lịch nghỉ của team, số liệu tổng hợp ẩn danh (k-anonymity), và phê duyệt yêu cầu từ tuyến báo cáo [Q2].
- **Lãnh đạo đơn vị & Ban điều hành (Unit Head, BU CEO, CFO, CHRO, CEO)**: Truy cập báo cáo nhân sự, tỷ lệ nghỉ việc, biến động headcount, quỹ lương và ngân sách theo phạm vi quản lý [Q2].
- **Khối nghiệp vụ chuyên trách (HRBP, C&B, Tài chính, IT Helpdesk)**: Tra cứu chuyên sâu phục vụ nghiệp vụ theo phân quyền được giao [Q2].
- **Quản trị nền tảng (Platform Admin) & Kiểm toán (Auditor)**: Giám sát vận hành và kiểm toán nhật ký truy cập nhạy cảm mà không vi phạm nguyên tắc bảo mật dữ liệu nhân sự [Q2].

## Success Metrics
Dự án được đánh giá thành công dựa trên các tiêu chí định lượng và an toàn bảo mật [Q3]:
1. **An toàn dữ liệu tuyệt đối (100%)**: 0% rò rỉ dữ liệu C3 (Lương cá nhân, thông tin nhạy cảm) thông qua prompt injection hoặc suy ngược dữ liệu [Q3].
2. **Hiệu năng & Trải nghiệm**: Thời gian phản hồi streaming hội thoại đạt dưới 3 giây; đánh giá người dùng đạt trên 90% phản hồi tích cực (thumbs up) [Q3].
3. **Thực thi phân quyền (ABAC)**: Đạt 100% độ chính xác trong việc thực thi chính sách ở tầng dữ liệu trước khi dữ liệu được chuyển tới LLM [Q3].
4. **Kiểm toán toàn diện**: 100% các truy vấn dữ liệu nhạy cảm C3 và các yêu cầu bị từ chối được ghi log kiểm toán đầy đủ (`data_access_log`) [Q3].

## Initiative Trigger
Chuyển đổi số tập đoàn đa ngành (Sao Mai Group) đòi hỏi hiện đại hóa công cụ làm việc số, đồng thời đáp ứng các tiêu chuẩn bảo mật dữ liệu cá nhân theo quy định pháp lý (như Nghị định 13/2023/NĐ-CP và đánh giá tác động bảo vệ dữ liệu cá nhân DPIA) [Q4].

## Initial Scope Signal
- **Workflow Scope**: `enterprise` [scope]
- **Confirmed Product Boundaries**:
  - KHÔNG sử dụng Text-to-SQL trực tiếp vào cơ sở dữ liệu nhân sự hoặc tài chính [Q6].
  - KHÔNG cho phép LLM tự động thay đổi lương hoặc thực hiện giao dịch tài chính tự động mà không qua quy trình phê duyệt của con người (Human-in-the-loop) [Q6].
  - Phiên bản v1 tập trung vào các kết nối dữ liệu chuẩn hóa nội bộ và RAG lai BM25 + Vector; chưa bao gồm tự động ghi trực tiếp (direct write-back) vào hệ thống ERP/SAP lõi [Q6].

## Assumptions & Open Questions
None. [Q1, Q2, Q3, Q4, Q5, Q6]
