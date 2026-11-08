# Code Generation Summary: Vietnamese Hybrid RAG (U-04)

## 1. Implemented Components
- **`app/rag/service.py`**:
  - `RagService`: Quản lý nạp tài liệu, tách chunk, lập chỉ mục BM25 và Vector.
  - `search()`: Thực hiện tìm kiếm kép BM25 + Vector, lọc Document ACL (`roles`, `units`, `min_level`), và hợp nhất kết quả bằng RRF (Reciprocal Rank Fusion).
- **`app/rag/text.py`**:
  - `tokenize_vietnamese()`: Xử lý tách từ tiếng Việt có dấu và không dấu, loại bỏ stop words, chuẩn hóa dấu thanh.
  - Thuật toán BM25 Okapi tính toán điểm số phù hợp từ khóa chính xác.
- **`app/rag/parsing.py`**:
  - Trích xuất văn bản tự động từ các định dạng: `.pdf` (pypdf), `.docx` (python-docx), `.csv`, `.md`, `.txt`.
- **`app/tools/knowledge.py`**:
  - `search_knowledge`: Công cụ gọi RAG tích hợp vào các Specialist Agent.
