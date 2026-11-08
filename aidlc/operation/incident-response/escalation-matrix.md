# Incident Escalation Matrix

| Cấp độ sự cố (Severity) | Thời gian phản hồi (MTTA) | Thời gian xử lý mục tiêu (MTTR) | Người tiếp nhận cấp 1 (L1) | Người chịu trách nhiệm cấp 2 (L2) | Thẩm quyền leo thang cao nhất (L3) |
|---|---|---|---|---|---|
| **SEV-1 (Khẩn cấp)**: Rò rỉ dữ liệu lương C3, lỗ hổng bypass ABAC, sập toàn bộ hệ thống chat | < 15 phút | < 2 giờ | On-call DevOps / SecOps | Tech Lead + Solution Architect | Group CEO, CHRO, Head of Security |
| **SEV-2 (Nghiêm trọng)**: LLM chính gián đoạn kéo dài, RAG không trả lời được, lỗi duyệt đơn | < 30 phút | < 4 giờ | AI Platform Engineer | Lead AI Engineer | CIO / IT Director |
| **SEV-3 (Trung bình)**: Một agent trả lời chậm, lỗi trích xuất tài liệu dạng hiếm, sai số liệu k-anonymity nhỏ | < 2 giờ | < 1 ngày làm việc | Support Helpdesk | Module Developer | Product Owner |
| **SEV-4 (Thấp)**: Lỗi giao diện nhỏ, góp ý chỉnh sửa câu chữ prompt | < 1 ngày | Theo Sprint tiếp theo | Support Helpdesk | Frontend / BA | Product Owner |
