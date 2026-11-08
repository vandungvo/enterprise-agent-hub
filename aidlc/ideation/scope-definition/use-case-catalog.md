# Catalog use case - Trợ lý nội bộ doanh nghiệp

Bối cảnh: tập đoàn công nghệ nhiều khối kinh doanh (demo: *Sao Mai Group*, hư cấu). Một chatbot duy nhất là "cửa trước" cho mọi nhân viên; router chuyển câu hỏi tới agent chuyên môn; dữ liệu trả về luôn bị giới hạn bởi quyền của người hỏi.

**Trạng thái**: ✅ có trong bản demo · 🔜 roadmap (đã có kiến trúc, cần thêm tool/connector)
**Phân loại dữ liệu**: C0 Công khai · C1 Nội bộ · C2 Mật · C3 Tuyệt mật

## Persona

| Persona | Ví dụ tài khoản demo | Cần gì từ trợ lý |
|---|---|---|
| Nhân viên | `dev.alpha`, `newbie` | Tự phục vụ: chính sách, lương của mình, phép, IT, chi phí |
| Quản lý trực tiếp | `manager.alpha` | Như nhân viên + lịch vắng mặt, phép, số liệu tổng hợp của team, duyệt yêu cầu |
| Lãnh đạo khối (BU CEO) | `head.games` | Số liệu nhân sự / ngân sách của khối, xu hướng, cảnh báo |
| CEO tập đoàn | `ceo` | Bức tranh toàn tập đoàn: headcount, nghỉ việc, quỹ lương, ngân sách; tài liệu chiến lược |
| HRBP | `hrbp.games` | Hồ sơ, phép, số liệu của khối mình phụ trách |
| C&B / CHRO | `cnb`, `chro` | Lương cá nhân (có audit), phân tích quỹ lương, kiểm toán truy cập |
| Tài chính | `cfo`, `finance.pay` | Ngân sách, chi phí theo phạm vi |
| Quản trị nền tảng | `itadmin` | Cấu hình agent, KB, theo dõi vận hành - **không** xem dữ liệu nhân sự |

## A. Thông tin tập đoàn & tri thức (C1)

| # | Use case | Ai | Trạng thái | Cách đáp ứng |
|---|---|---|---|---|
| A1 | Giới thiệu tập đoàn, công ty thành viên, lịch sử, văn phòng | Mọi người | ✅ | RAG `company` |
| A2 | Nội quy, sổ tay nhân viên, quy tắc ứng xử, bảo mật | Mọi người | ✅ | RAG |
| A3 | Tìm đồng nghiệp (tên, chức danh, đơn vị, email, quản lý) | Mọi người | ✅ | `directory_search` (chỉ trường công khai nội bộ) |
| A4 | Sơ đồ tổ chức, ai phụ trách khối nào | Mọi người | ✅ | `get_org_chart` |
| A5 | Tin tức nội bộ, thông báo, sự kiện | Mọi người | 🔜 | Connector CMS/intranet |
| A6 | Tài liệu chỉ dành cho quản lý / ban điều hành | Quản lý, exec | ✅ | KB `leadership` + ACL từng tài liệu (roles, min_level) |

## B. Hồ sơ cá nhân (C2-C3)

| # | Use case | Ai | Trạng thái | Cách đáp ứng |
|---|---|---|---|---|
| B1 | Xem hồ sơ của mình (ngày vào làm, cấp bậc, người phụ thuộc, CCCD…) | Bản thân | ✅ | `get_employee_profile` |
| B2 | Quản lý xem thông tin công việc của tuyến báo cáo | Quản lý | ✅ | Phần `employment`; phần `personal` bị ẩn |
| B3 | HRBP xem hồ sơ đầy đủ trong khối phụ trách | HRBP | ✅ | `profile.personal` scope = khối, có audit |
| B4 | Cập nhật thông tin cá nhân (địa chỉ, tài khoản ngân hàng, người phụ thuộc) | Bản thân | 🔜 | Tool có phê duyệt C&B |
| B5 | Xin giấy xác nhận công tác / thu nhập | Bản thân | 🔜 | Sinh văn bản mẫu + duyệt HR |
| B6 | "Ai đã xem dữ liệu nhạy cảm của tôi?" | Bản thân | ✅ | Trang *Quyền của tôi* (`/api/my-data-access`) |

## C. Lương, thưởng, thuế, bảo hiểm (C3)

| # | Use case | Ai | Trạng thái | Cách đáp ứng |
|---|---|---|---|---|
| C1 | Xem / giải thích phiếu lương (gross, BH, giảm trừ, thuế TNCN, thực nhận) | Bản thân | ✅ | `get_payslip` |
| C2 | So sánh lương giữa các kỳ, vì sao tháng này khác tháng trước | Bản thân | ✅ | `get_payslip` nhiều kỳ |
| C3 | Lịch sử điều chỉnh lương | Bản thân, C&B | ✅ | `get_compensation_history` |
| C4 | Chính sách thưởng, lương 13, phúc lợi, bảo hiểm sức khỏe | Mọi người | ✅ | RAG `people_policy` |
| C5 | Ước tính lương net từ gross / tác động khi thêm người phụ thuộc | Bản thân | 🔜 | Tool tính toán dùng cùng công thức payroll |
| C6 | Quyết toán thuế TNCN, chứng từ khấu trừ thuế | Bản thân | 🔜 | Connector payroll |
| C7 | C&B tra cứu lương cá nhân phục vụ nghiệp vụ | C&B, CHRO | ✅ | Có audit nhạy cảm |
| C8 | Quản lý hỏi lương của nhân viên | Quản lý | ✅ (bị từ chối) | Chỉ được số tổng hợp, ẩn nhóm < 5 người |

## D. Thời gian & nghỉ phép (C2)

| # | Use case | Ai | Trạng thái | Cách đáp ứng |
|---|---|---|---|---|
| D1 | Còn bao nhiêu ngày phép, phép chuyển sang, ngày nghỉ ốm | Bản thân | ✅ | `get_leave_balance` |
| D2 | Nộp đơn nghỉ (kiểm tra số dư, tính ngày làm việc) | Bản thân | ✅ | `submit_leave_request` → **quản lý trực tiếp** duyệt |
| D3 | Lịch sử đơn nghỉ | Bản thân | ✅ | `list_leave_requests` |
| D4 | Ai trong team vắng tuần này | Đồng nghiệp, quản lý | ✅ | `team_calendar` (đồng nghiệp không thấy loại nghỉ) |
| D5 | Hủy / sửa đơn nghỉ | Bản thân | 🔜 | Tool + duyệt |
| D6 | Đăng ký OT, WFH; giải trình chấm công | Bản thân | 🔜 | Connector chấm công |

## E. Quản lý (manager self-service)

| # | Use case | Ai | Trạng thái | Cách đáp ứng |
|---|---|---|---|---|
| E1 | Duyệt đơn nghỉ / chi phí / ticket của tuyến báo cáo | Quản lý | ✅ | Hàng đợi *Phê duyệt*, định tuyến theo quan hệ báo cáo |
| E2 | Số dư phép, đơn nghỉ của từng thành viên | Quản lý | ✅ | `get_leave_balance`, `list_leave_requests(scope=team)` |
| E3 | Headcount, nghỉ việc, ngày phép đã dùng của team | Quản lý | ✅ | `workforce_analytics` (scope = tuyến báo cáo) |
| E4 | Lương trung bình / quỹ lương của team | Quản lý | ✅ | Ẩn nhóm < 5, ẩn bổ sung chống suy ngược |
| E5 | Ngân sách đơn vị vs thực tế | Trưởng đơn vị | ✅ | `budget_report` |
| E6 | Chuẩn bị review hiệu suất, gợi ý phản hồi | Quản lý | 🔜 | Connector performance + hướng dẫn |

## F. Lãnh đạo / CEO

| # | Câu hỏi mẫu | Trạng thái | Dữ liệu được dùng |
|---|---|---|---|
| F1 | "Headcount từng khối hiện tại? Tuyển mới / nghỉ việc 12 tháng qua?" | ✅ | `workforce.aggregate` toàn tập đoàn |
| F2 | "Tỷ lệ nghỉ việc theo khối, khối nào đáng lo?" | ✅ | `attrition_rate` group_by bu |
| F3 | "Quỹ lương 6 tháng gần nhất theo khối, xu hướng theo tháng?" | ✅ | `compensation.aggregate` (k=3) |
| F4 | "Ngân sách các khối đang vượt hay dưới kế hoạch?" | ✅ | `finance.budget` |
| F5 | "Lương của CEO Sao Mai Games?" | ✅ | Được, vì là cấp dưới trực tiếp (có audit) |
| F6 | "Lương của một kỹ sư ở Studio Alpha?" | ✅ (bị từ chối) | CEO chỉ xem tổng hợp với nhân viên cấp dưới gián tiếp |
| F7 | "Định hướng chiến lược 2027 nói gì về Cloud?" | ✅ | Tài liệu C3, ACL `roles: [exec]` |
| F8 | Doanh thu, lợi nhuận, KPI kinh doanh theo khối | 🔜 | Connector ERP / data warehouse + policy `finance.pnl` |
| F9 | Báo cáo tự động hằng tuần gửi Ban điều hành | 🔜 | Lịch chạy định kỳ + cùng policy engine |

## G. HRBP / C&B / CHRO

| # | Use case | Trạng thái |
|---|---|---|
| G1 | Phân tích nghỉ việc theo đơn vị / cấp bậc trong khối phụ trách | ✅ |
| G2 | Phân tích phân bổ lương theo cấp bậc (C&B: không ẩn nhóm) | ✅ |
| G3 | Kiểm toán truy cập dữ liệu nhạy cảm, các lần bị từ chối | ✅ (vai trò `auditor`) |
| G4 | Soạn / cập nhật chính sách vào knowledge base có phân loại | ✅ |
| G5 | Mô phỏng ngân sách tăng lương | 🔜 |

## H. Tài chính & chi phí

| # | Use case | Trạng thái |
|---|---|---|
| H1 | Định mức công tác phí, tiếp khách, thẩm quyền chi | ✅ RAG `finance_policy` |
| H2 | Nộp đề nghị thanh toán: ≤ 20 triệu thì quản lý duyệt, > 20 triệu thì CEO khối duyệt | ✅ `submit_expense_claim` |
| H3 | Theo dõi đề nghị thanh toán của mình / team | ✅ `list_expense_claims` |
| H4 | Trạng thái PO, hóa đơn nhà cung cấp | 🔜 Connector ERP |
| H5 | Đọc hóa đơn từ ảnh (OCR) để tự điền đề nghị | 🔜 Claude vision |

## I. IT & bảo mật

| # | Use case | Trạng thái |
|---|---|---|
| I1 | VPN, mật khẩu, MFA, email: hướng dẫn tự xử lý | ✅ |
| I2 | Tạo ticket sự cố / yêu cầu cấp quyền | ✅ `create_ticket` |
| I3 | Báo cáo phishing / sự cố bảo mật khẩn | ✅ (ticket critical) |
| I4 | Tra trạng thái ticket, SLA | 🔜 Connector Jira/ServiceNow |
| I5 | Cấp quyền tự động sau khi duyệt (IAM) | 🔜 |

## J. Hành chính - văn phòng · K. Tuyển dụng & vòng đời nhân viên · L. Học tập · M. Pháp chế

| # | Use case | Trạng thái |
|---|---|---|
| J1 | Đặt phòng họp, chỗ đỗ xe, đăng ký khách | 🔜 Connector lịch / facility |
| J2 | Văn phòng phẩm, sửa chữa, vệ sinh | 🔜 ticket `facility` |
| K1 | Onboarding: checklist tuần đầu, khóa học bắt buộc | ✅ RAG (`newbie` dùng thử) |
| K2 | Vị trí đang tuyển, giới thiệu ứng viên (referral) | 🔜 Connector ATS |
| K3 | Offboarding: bàn giao, trả tài sản, phỏng vấn nghỉ việc | ✅ RAG / 🔜 workflow |
| L1 | Lộ trình học, đăng ký khóa học, ngân sách đào tạo còn lại | 🔜 Connector LMS |
| M1 | Mẫu hợp đồng, quy trình ký, tra cứu điều khoản | 🔜 KB `legal` có ACL |
| M2 | Khai báo xung đột lợi ích, kênh Speak-Up | ✅ RAG / 🔜 form ẩn danh |

## N. Quản trị nền tảng AI

| # | Use case | Trạng thái |
|---|---|---|
| N1 | Thêm / sửa agent, KB, quyền dùng agent không cần sửa code | ✅ `config/platform.yaml` |
| N2 | Sửa chính sách dữ liệu, áp dụng ngay | ✅ `config/policies.yaml` + *Tải lại cấu hình* |
| N3 | Theo dõi mức sử dụng, chi phí, độ trễ, feedback theo khối | ✅ trang *Mức độ sử dụng AI* |
| N4 | Audit log vận hành (đã che kết quả tool nhạy cảm) | ✅ |
| N5 | Bộ eval: câu hỏi chuẩn + câu hỏi tấn công (prompt injection) chạy trước mỗi lần đổi prompt / model | 🔜 |

## Ưu tiên triển khai đề xuất

1. **Wave 1 (giá trị cao, rủi ro thấp)**: A, I, H1, K1. Chỉ dùng RAG nội bộ, chưa đụng dữ liệu cá nhân, giảm ngay tải cho HR và IT.
2. **Wave 2 (self-service)**: B1, C1-C4, D1-D4, E1-E2. Cần SSO, HRIS connector, policy engine, audit.
3. **Wave 3 (lãnh đạo)**: E3-E5, F, G. Cần data warehouse, k-anonymity, review pháp chế / DPO.
4. **Wave 4 (tự động hóa)**: các workflow 🔜 có ghi dữ liệu (B4, D5, H4, I5), báo cáo định kỳ.

KPI đo hiệu quả: tỷ lệ nhân viên dùng hằng tháng (adoption), % câu hỏi tự giải quyết không cần chuyển HR/IT, thời gian xử lý yêu cầu (đơn nghỉ, chi phí), mức hài lòng (feedback), chi phí trên mỗi câu hỏi, số truy cập bị chặn và sự cố rò rỉ (mục tiêu 0).
