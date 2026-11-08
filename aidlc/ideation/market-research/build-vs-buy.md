# Build vs Buy Assessment

## Decision Drivers & Strategic Rationale

| Yếu tố đánh giá | Phương án Mua (Buy SaaS - Glean/MS Copilot) | Phương án Tự xây dựng (Build In-House) | Phân tích & Lựa chọn | Nguồn |
|---|---|---|---|---|
| **Tuân thủ & Bảo vệ dữ liệu (DPIA, NĐ 13)** | Rủi ro lưu trữ dữ liệu tại cloud nước ngoài của bên thứ 3; khó ký thỏa thuận Zero Data Retention tùy biến. | Toàn quyền kiểm soát lưu trữ, mã hóa tại chỗ (VPC riêng), kiểm toán 100% truy cập dữ liệu cá nhân. | **Build vượt trội** | [Q2] |
| **Logic phân quyền phức tạp (ABAC)** | Thường chỉ hỗ trợ RBAC đơn giản hoặc đồng bộ quyền thư mục. Khó áp dụng logic tuyến báo cáo HRIS động. | Xây dựng policy engine Python độc lập, tính toán quyền tức thời theo quan hệ quản lý và k-anonymity. | **Build vượt trội** | [Q1, Q2] |
| **Chi phí dài hạn (TCO)** | Trả phí thuê bao trên đầu người (user/month) rất tốn kém khi quy mô tập đoàn lên tới hàng ngàn nhân sự. | Chi phí phát triển ban đầu + chi phí token theo mức độ sử dụng thực tế (Pay-as-you-go). Tiết kiệm chi phí bản quyền định kỳ. | **Build tối ưu chi phí** | [Q2] |
| **Khả năng mở rộng & Tích hợp nội bộ** | Phụ thuộc vào kho connector của nhà cung cấp; khó tích hợp các hệ thống HRIS/ERP tự xây dựng của tập đoàn. | Tự do bổ sung các tool Pydantic, agent chuyên môn và kết nối trực tiếp cơ sở dữ liệu nội bộ. | **Build linh hoạt** | [Q2, Q3] |
| **Rủi ro phụ thuộc công nghệ (Vendor Lock-in)** | Bị khóa chặt vào hệ sinh thái của Microsoft hoặc OpenAI. | Adapter trừu tượng hóa cho phép đổi model (Claude, Gemini, DeepSeek, Ollama) chỉ bằng đổi cấu hình. | **Build bền vững** | [Q2] |

## Conclusion
Quyết định chiến lược: **Tự xây dựng (Build In-house)** nền tảng Enterprise Agent Hub với kiến trúc module mở, tận dụng các mô hình ngôn ngữ lớn thương mại hàng đầu thông qua API bảo mật hoặc mô hình tự host, đồng thời giữ quyền kiểm soát tuyệt đối tầng dữ liệu và phân quyền [Q2].

## Assumptions & Open Questions
None. [Q1, Q2]
