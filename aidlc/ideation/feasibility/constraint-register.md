# Constraint Register

## 1. Technical Constraints

| Constraint ID | Category | Description | Rationale / Impact | Source |
|---|---|---|---|---|
| TC-01 | Architecture | Không sử dụng Text-to-SQL tự do trên dữ liệu nhân sự và tài chính | Tránh rủi ro SQL Injection và rò rỉ dữ liệu ngoài phạm vi policy | [intent] |
| TC-02 | Security | Principal phải được tái cấu trúc (reconstructed) ở mỗi HTTP request từ HRIS | Ngăn chặn việc sử dụng quyền cũ khi nhân viên đổi vai trò hoặc đã nghỉ việc | [Q1] |
| TC-03 | Privacy | K-Anonymity với ngưỡng k >= 3 hoặc k >= 5 và complementary suppression cho số liệu tổng hợp | Chống kỹ thuật suy ngược số liệu cá nhân của các nhóm nhân sự nhỏ | [intent] |
| TC-04 | Logging | Che mờ (masking/redaction) hoàn toàn kết quả trả về của các tool C3 trước khi ghi log vận hành | Bảo vệ thông tin lương và dữ liệu cá nhân khỏi sự tò mò của Platform Admin | [Q2] |
| TC-05 | Database | Production bắt buộc sử dụng PostgreSQL có cấu hình RLS và mã hóa at-rest | Đảm bảo tính toàn vẹn và bảo mật dữ liệu doanh nghiệp | [Q1] |

## 2. Regulatory & Compliance Constraints

| Constraint ID | Category | Description | Compliance Standard | Source |
|---|---|---|---|---|
| RC-01 | Data Protection | Thực hiện đánh giá tác động xử lý dữ liệu cá nhân (DPIA) trước khi golive | Nghị định 13/2023/NĐ-CP (Việt Nam) | [Q2] |
| RC-02 | Vendor Policy | Ký cam kết Zero Data Retention (ZDR) với nhà cung cấp LLM qua API | Chính sách AI có trách nhiệm & DPA | [Q2] |
| RC-03 | Data Retention | Tự động thanh trừng các phiên hội thoại chạm dữ liệu C3 sau 30 ngày (`SENSITIVE_RETENTION_DAYS`) | Nguyên tắc lưu trữ có thời hạn của luật bảo vệ dữ liệu | [Q2] |

## 3. Operational & Governance Constraints

| Constraint ID | Category | Description | Impact | Source |
|---|---|---|---|---|
| OC-01 | Human in the loop | Các hành động tạo tác động (nghỉ phép, xin tiền, tạo ticket) bắt buộc đưa vào hàng đợi phê duyệt | Cần người quản lý duyệt theo tuyến báo cáo trước khi ghi nhận trạng thái cuối | [intent] |
| OC-02 | Platform Admin | Quyền Platform Admin bị cô lập hoàn toàn khỏi quyền xem dữ liệu nhân sự nghiệp vụ | Tách bạch quyền hạn quản trị hạ tầng và quyền truy cập dữ liệu nghiệp vụ | [intent] |

## Assumptions & Open Questions
None. [Q1, Q2, Q3]
