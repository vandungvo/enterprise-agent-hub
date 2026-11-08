# Business Overview & Context

## 1. Domain & Industry Context
- **Doanh nghiệp**: Tập đoàn Sao Mai Group (Doanh nghiệp hư cấu mô phỏng tập đoàn công nghệ đa ngành: Games, Pay, Cloud, và các đơn vị chức năng tập đoàn).
- **Quy mô demo**: ~100 nhân sự trải rộng trên các công ty con và phòng ban, cấu trúc tổ chức phân tầng từ Team -> Phòng -> Khối (Business Unit) -> Tập đoàn.
- **Thực trạng nghiệp vụ**: Nhân viên phải tương tác với nhiều hệ thống riêng lẻ để tra cứu thông tin nhân sự (HRIS), chính sách C&B, quy định tài chính, ticket IT và báo cáo ngân sách. Các nhà quản lý mất nhiều thời gian tổng hợp báo cáo và duyệt yêu cầu.

## 2. Business Objectives
1. **Một cửa duy nhất (Single Door)**: Cung cấp 1 chatbot duy nhất cho toàn thể cán bộ nhân viên giải quyết mọi thắc mắc và tác vụ tự phục vụ (Self-service).
2. **Bảo mật dữ liệu tuyệt đối (Zero-Leak)**: Kiểm soát nghiêm ngặt ranh giới dữ liệu cá nhân (đặc biệt là lương C3, đánh giá hiệu suất, bảo hiểm) theo nguyên tắc Need-to-know, ngăn chặn mọi nỗ lực prompt injection hoặc suy ngược dữ liệu.
3. **Minh bạch và tuân thủ**: Tự động ghi log kiểm toán truy cập dữ liệu nhạy cảm, cho phép nhân viên xem ai đã truy cập dữ liệu của mình, hỗ trợ đánh giá DPIA theo Nghị định 13/2023/NĐ-CP.
4. **Nâng cao năng suất**: Tự động hóa giải đáp thắc mắc thường gặp, giảm 70-80% khối lượng công việc lặp lại của HR, IT Helpdesk và Kế toán.

## 3. Key Business Personas
- **Nhân viên (`employee`)**: Tra cứu phiếu lương, số dư phép, chính sách, nộp đơn nghỉ, tạo ticket IT.
- **Quản lý (`manager`)**: Xem lịch vắng của team, số liệu tổng hợp (k-anonymity), duyệt đơn của cấp dưới.
- **Lãnh đạo đơn vị (`unit_head`, `exec`, `ceo`)**: Xem báo cáo biến động nhân sự, tỷ lệ nghỉ việc, quỹ lương và ngân sách theo phạm vi quản lý.
- **Chuyên viên nghiệp vụ (`hrbp`, `cnb`, `finance`, `it_support`)**: Thực hiện các tác vụ nghiệp vụ chuyên môn trong phạm vi được ủy quyền.
- **Kiểm toán (`auditor`)**: Giám sát toàn bộ nhật ký truy cập nhạy cảm và các lần từ chối vi phạm policy.
- **Quản trị (`platform_admin`)**: Quản lý cấu hình agent, KB, theo dõi chi phí/token nhưng không được quyền xem dữ liệu nhân sự.
