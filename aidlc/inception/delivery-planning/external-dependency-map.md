# External Dependency Map

| External Entity | Integration Interface | Criticality | Fallback Strategy |
|---|---|---|---|
| **Anthropic Claude API** | Messages API (`/v1/messages`) | Critical (Primary) | Tự động retry backoff theo Retry-After; Fallback sang Gemini hoặc OpenAI adapter |
| **Google Gemini API** | REST API (`generativelanguage.googleapis.com`) | High (Secondary) | Fallback sang Claude hoặc Local Ollama |
| **Corporate HRIS Database** | Direct SQL / Read Replica | Critical | Cache danh sách cấu trúc tổ chức tạm thời nếu DB bảo trì |
| **Corporate SSO (OIDC)** | OIDC Authorization Code Flow | High | Cho phép phiên dự phòng qua Token bảo mật nội bộ |
| **FastEmbed Local Models** | Local filesystem ONNX models | Medium | Fallback về Pure BM25 Lexical search nếu thiếu thư viện FastEmbed |
