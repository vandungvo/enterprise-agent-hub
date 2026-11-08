# Cost Analysis & Prompt Caching Optimization

## 1. Cost Dynamics & Token Efficiency
Hệ thống sử dụng cơ chế **Prompt Caching** của Anthropic Claude để tối ưu hóa chi phí token:
- Các thành phần cố định trong System Prompt của Router và các Specialist Agent (danh mục tool, hướng dẫn nghiệp vụ, nguyên tắc bảo mật) chiếm ~3,000 - 5,000 tokens mỗi lượt gọi.
- Khi bật prompt caching, các token này chỉ bị tính phí cache write một lần và giảm 90% chi phí đọc (cache read) ở các lượt gọi tiếp theo trong vòng đời 5 phút.

## 2. Cost Projection per Month (Tập đoàn 100 nhân sự demo)
- Trung bình mỗi nhân viên thực hiện 5 câu hỏi/ngày = 500 câu hỏi/ngày.
- Chi phí token thô (không có prompt caching): ~$25 - $35 / ngày (~$750 - $1,050 / tháng).
- Chi phí token thực tế (có prompt caching + RAG token reduction): ~$6 - $10 / ngày (~$180 - $300 / tháng).
- **Tỷ lệ tiết kiệm**: Đạt tới ~70% chi phí vận hành mô hình ngôn ngữ lớn.

## 3. Recommendations for Future Cost Optimization
1. Chuyển các tác vụ đơn giản (tìm kiếm danh bạ, lấy giờ hiện tại, chào hỏi) sang mô hình nhẹ hơn (`claude-3-5-haiku` hoặc `gemini-2.0-flash`).
2. Tự host mô hình LLM mã nguồn mở (DeepSeek / Qwen / Llama 3) qua Ollama hoặc vLLM trong mạng nội bộ cho các nghiệp vụ nội bộ thường ngày.
