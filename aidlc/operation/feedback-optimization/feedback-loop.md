# Feedback Loop & Continuous Improvement

## 1. User Feedback Channels
- **In-App Rating**: Mỗi câu trả lời của AI có nút 👍 (Hài lòng) và 👎 (Chưa hài lòng) kèm hộp thoại nhập lý do (Câu trả lời thiếu chính xác, Trích dẫn sai nguồn, Chưa hiểu ý, Không đủ quyền).
- **Weekly Review Meeting**: Đội ngũ phát triển (AI Engineer, BA) và đại diện phòng Nhân sự rà soát các câu trả lời bị đánh giá 👎.

## 2. Feedback Taxonomy & Corrective Actions
1. **Lỗi trích dẫn RAG (Hallucination hoặc tìm sai tài liệu)**:
   - Cập nhật tài liệu nguồn trong Knowledge Base; bổ sung từ khóa đồng nghĩa tiếng Việt vào `text.py`.
2. **Lỗi điều phối Router Agent (Sai domain agent)**:
   - Tinh chỉnh mô tả nhiệm vụ của agent trong `config/platform.yaml` và reload.
3. **Phản hồi về phân quyền quá chặt hoặc quá lỏng**:
   - Chuyển tiếp cho Ban chính sách và C&B xem xét điều chỉnh trong `config/policies.yaml`.

## 3. Policy Evolution & Knowledge Expansion
- Định kỳ hằng quý: Rà soát lại toàn bộ các tài liệu trong 5 Knowledge Base, gỡ bỏ các văn bản hết hiệu lực.
- Kiểm toán an toàn: Thực hiện đợt diễn tập Red-team để kiểm tra các biến thể prompt injection mới nhất.
