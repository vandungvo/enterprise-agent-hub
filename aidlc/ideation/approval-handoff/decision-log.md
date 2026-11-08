# Ideation Phase Decision Log

| Quyết định ID | Thời gian | Hạng mục | Quyết định đã chốt | Cơ sở / Lý do | Người quyết định |
|---|---|---|---|---|---|
| DEC-01 | 2026-11-08 | Scope Profile | Áp dụng hồ sơ vòng đời `enterprise` với đầy đủ 5 Phase và 30 Stage | Yêu cầu mức độ kiểm soát, truy xuất nguồn gốc và bảo mật cao nhất | Steering Committee |
| DEC-02 | 2026-11-08 | Chiến lược Build | Tự xây dựng (Build in-house) nền tảng thay vì mua SaaS | Bảo mật dữ liệu lương C3, kiểm soát ABAC ở data tier và tránh vendor lock-in | Architecture Board |
| DEC-03 | 2026-11-08 | Bảo mật Lương & Dữ liệu C3 | Phân quyền nằm ở data tier (Python policy engine), không phụ thuộc system prompt; áp dụng K-anonymity và complementary suppression | Chống triệt để các kỹ thuật prompt injection và suy ngược số liệu | Security & C&B Lead |
| DEC-04 | 2026-11-08 | LLM Provider | Hỗ trợ đa nhà cung cấp (Claude, Gemini, OpenAI-compat, Ollama) qua adapter chuẩn hóa | Linh hoạt chi phí, chống phụ thuộc một bên duy nhất và sẵn sàng cho mô hình on-premise | Lead Architect |
| DEC-05 | 2026-11-08 | Lộ trình Database | Chuyển dịch từ SQLite demo sang PostgreSQL kết hợp Row-Level Security (RLS) khi lên Production | Tạo lớp phòng ngự chiều sâu (Defense-in-depth) | DevOps & SecOps |
