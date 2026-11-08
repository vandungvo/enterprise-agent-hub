# Enterprise Initiative Brief: Enterprise Agent Hub

## 1. Executive Summary
- **Tên sáng kiến**: Enterprise Agent Hub (Trợ lý AI nội bộ cho Tập đoàn đa khối).
- **Phạm vi vòng đời**: `enterprise` (30 stages, toàn diện 5 phases).
- **Mục tiêu cốt lõi**: Xây dựng "cửa trước" thông minh duy nhất phục vụ toàn thể cán bộ nhân viên và lãnh đạo tập đoàn tra cứu thông tin (HR, Lương, Phép, Tài chính, IT, Sơ đồ tổ chức), với cam kết an toàn bảo mật tuyệt đối thông qua cơ chế phân quyền ABAC tại tầng dữ liệu, không phụ thuộc vào prompt engineering.

## 2. Key Pillars of the Solution
1. **Multi-Agent Architecture**: Router agent tiếp nhận, phân tích intent và giao quyền xử lý cho 5 agent chuyên môn (`people`, `insights`, `finance`, `it_helpdesk`, `company_info`).
2. **Deterministic Data-Tier ABAC**: Quyền hạn `Principal` được tái tạo ở từng HTTP request từ HRIS; quy tắc chính sách tập trung trong `config/policies.yaml`.
3. **Data Protection & Privacy**:
   - Dữ liệu lương C3 chỉ hiển thị cho chính chủ hoặc cấp quản lý trực tiếp (kèm audit).
   - K-anonymity (k=3, k=5) và Complementary Suppression cho số liệu tổng hợp.
   - Không hỗ trợ Text-to-SQL tự do.
   - Tự động xóa hội thoại C3 sau 30 ngày.
4. **Hybrid Vietnamese RAG**: Tìm kiếm kết hợp BM25 + Embeddings với phân quyền ACL đến từng tài liệu (`roles`, `units`, `min_level`).
5. **Human-in-the-Loop (HITL)**: Đơn nghỉ phép, đề nghị thanh toán và ticket IT đều có hàng đợi phê duyệt định tuyến theo quan hệ quản lý.
6. **Multi-Provider Resilience**: Tương thích hoàn toàn với Claude (Messages API), Gemini và các API chuẩn OpenAI (Ollama, Groq, OpenRouter).

## 3. Feasibility & Risk Verdict
- **Tính khả thi kỹ thuật**: Rất cao, đã có sản phẩm chạy thực tế kiểm chứng.
- **Tuân thủ pháp lý**: Phù hợp định hướng Nghị định 13/2023/NĐ-CP (DPIA) và cam kết Zero Data Retention từ các nhà cung cấp LLM.
- **Lộ trình dài hạn**: Nâng cấp cơ sở dữ liệu sang PostgreSQL RLS và tích hợp SSO OIDC tập đoàn.

## 4. Go / No-Go Decision
**KHUYẾN NGHỊ: GO (PHÊ DUYỆT BƯỚC VÀO PHASE 2: INCEPTION)**.
