# Stakeholder Map

## Key Stakeholders & Interests

| Stakeholder Role | Representative / Group | Primary Interests & Concerns | Authority Type | Source |
|---|---|---|---|---|
| Ban Giám đốc & CEO Tập đoàn | CEO, Phó TGĐ Điều hành | Bức tranh tổng thể về nhân sự, ngân sách, xu hướng nghỉ việc, tuân thủ pháp lý và hiệu quả đầu tư AI | Quyết định chiến lược & Ngân sách | [Q5] |
| Lãnh đạo Khối & Đơn vị (BU Heads) | BU CEO (Games, Pay, Cloud) | Tự chủ quản lý nhân sự, hiệu suất dự án, ngân sách khối, tốc độ phê duyệt | Quyết định phạm vi khối | [Q5] |
| Khối Nhân sự & Phúc lợi (HR/C&B) | CHRO, C&B Lead, HRBP | Bảo mật dữ liệu lương (C3), tính chính xác của phiếu lương, tuân thủ chính sách nhân sự | Quyết định chính sách nhân sự | [Q5] |
| Khối Tài chính Kế toán | CFO, Kế toán trưởng | Kiểm soát ngân sách, tính hợp lệ của đề nghị thanh toán/công tác phí | Quyết định quy định tài chính | [Q5] |
| Khối Công nghệ & Vận hành | Platform Admin, IT Lead | Tính ổn định của hệ thống, chi phí token LLM, tích hợp SSO/HRIS, không xem dữ liệu nhân sự | Quyết định kiến trúc & kỹ thuật | [Q5] |
| Pháp chế & Bảo vệ Dữ liệu | Pháp chế, Data Protection Officer | Tuân thủ Nghị định 13/2023/NĐ-CP, hồ sơ DPIA, hợp đồng xử lý dữ liệu (DPA) với bên cung cấp AI | Thẩm định & Giám sát tuân thủ | [Q5] |
| Người dùng cuối (Cán bộ nhân viên) | Toàn thể nhân viên | Giao diện tiện lợi, tra cứu nhanh, thông tin lương/phép cá nhân được bảo vệ nghiêm ngặt | Đối tượng thụ hưởng | [Q2] |

## Decision-Makers vs Influencers

| Entity | Role in Initiative | Scope of Influence / Decision | Source |
|---|---|---|---|
| Ban Điều hành (CEO, CFO, CHRO) | Decision-Maker | Phê duyệt phạm vi ngân sách, thông qua kiến trúc phân quyền và chính sách bảo mật dữ liệu | [Q5] |
| Hội đồng Kiến trúc & IT Admin | Decision-Maker | Quyết định lựa chọn mô hình LLM, framework triển khai, hạ tầng hosting và CI/CD | [Q5] |
| HRBP & Kế toán viên | Influencer | Đóng góp nghiệp vụ chi tiết, tiêu chuẩn dữ liệu và biểu mẫu phê duyệt | [Q5] |
| Cán bộ nhân viên | Influencer | Cung cấp phản hồi đánh giá trải nghiệm thực tế (thumbs up/down) | [Q3] |

## Communication Requirements & Cadence

| Stakeholder Group | Frequency | Channels | Key Content | Source |
|---|---|---|---|---|
| Ban Điều hành / CEO | Định kỳ hàng tháng | Dashboard Giám sát AI (`/usage`) & Báo cáo tổng hợp | Tỷ lệ chấp nhận, chi phí token, mức độ tuân thủ bảo mật, cảnh báo vi phạm | [Q3, Q5] |
| Quản lý trực tiếp | Theo thời gian thực | Web App (Hàng đợi Phê duyệt) & Email/Chat notification | Yêu cầu nghỉ phép, đề nghị thanh toán của nhân viên cấp dưới cần xử lý | [Q2] |
| Đội ngũ Vận hành / IT | Liên tục 24/7 | Log hệ thống, Metrics dashboard, Alarms | Độ trễ API, lỗi 429/500 từ LLM provider, cảnh báo suy giảm hiệu năng | [Q3] |
| Toàn thể Nhân viên | Định kỳ phát hành | Thông báo tập đoàn, Widget chatbot | Tính năng mới, cập nhật chính sách tri thức, hướng dẫn tự phục vụ | [Q1, Q2] |

## Assumptions & Open Questions
None. [Q1, Q2, Q3, Q4, Q5, Q6]
