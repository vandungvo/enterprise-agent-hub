# Deployment Strategy & Pipeline Specification

## 1. Deployment Topology & Containerization
Enterprise Agent Hub được đóng gói dưới dạng Docker Container chuẩn và triển khai trên hạ tầng Private Cloud hoặc VPC riêng:

```dockerfile
# Multi-stage Dockerfile
FROM python:3.11-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY config/ ./config/
COPY static/ ./static/
COPY seed_docs/ ./seed_docs/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

## 2. Release Strategy: Blue-Green / Rolling Update
- Áp dụng chiến lược **Rolling Update** (hoặc Blue-Green) với tối thiểu 2 replicas để đảm bảo tính sẵn sàng cao (High Availability).
- Healthcheck Endpoint: `GET /health` hoặc `GET /api/me` (đảm bảo container sẵn sàng trước khi nhận traffic).
- Quá trình chuyển đổi cấu hình nóng (`platform.yaml` và `policies.yaml`) được thực thi qua API `POST /api/admin/reload-config` mà không gây gián đoạn các kết nối streaming hiện tại.
