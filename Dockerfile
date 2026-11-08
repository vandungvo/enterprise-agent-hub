# Enterprise Agent Hub - production image (self-hosted / Kubernetes). Vercel does not use this file.
FROM python:3.13-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 LOG_FORMAT=json AGENTHUB_DATA_DIR=/app/data
WORKDIR /app
COPY --from=builder /install /usr/local
COPY app/ ./app/
COPY config/ ./config/
COPY static/ ./static/
COPY seed_docs/ ./seed_docs/
COPY migrations/ ./migrations/
COPY alembic.ini ./
RUN useradd --create-home --uid 10001 agenthub && mkdir -p /app/data && chown agenthub /app/data
USER agenthub
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=4).status == 200 else 1)"
# Migrations + seed run at startup under a PostgreSQL advisory lock, so several replicas can start together.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2", "--proxy-headers", "--forwarded-allow-ips=*"]
