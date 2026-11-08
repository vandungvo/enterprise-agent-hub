"""Logging, request correlation and HTTP security headers.

* Every request gets an id (incoming `X-Request-ID`, else Vercel's `x-vercel-id`, else a new uuid). It is
  returned in the `X-Request-ID` response header and attached to every log line written while handling it,
  so a user-reported error code leads straight to the server logs.
* One access-log line per request (method, path, status, duration) - for SSE, when the stream ends.
* LOG_FORMAT=json emits one JSON object per line (for log pipelines: Vercel log drains, Datadog, Loki...).
* Security headers on every response (CSP, nosniff, frame denial, referrer policy, HSTS on HTTPS).

Implemented as plain ASGI middleware (not BaseHTTPMiddleware) so streaming responses are untouched.
"""
from __future__ import annotations

import contextvars
import json
import logging
import time
import uuid

from app.core.settings import settings

request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("request_id", default="-")
access_log = logging.getLogger("agenthub.access")

# Scripts: same origin + the two pinned CDN libraries used by the UI (marked, DOMPurify, with SRI).
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; script-src 'self' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data:; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'self'; "
    "form-action 'self'; frame-ancestors 'none'"
)
SECURITY_HEADERS = [
    (b"x-content-type-options", b"nosniff"),
    (b"x-frame-options", b"DENY"),
    (b"referrer-policy", b"strict-origin-when-cross-origin"),
    (b"permissions-policy", b"camera=(), microphone=(), geolocation=()"),
    (b"content-security-policy", CONTENT_SECURITY_POLICY.encode()),
]
HSTS = (b"strict-transport-security", b"max-age=31536000; includeSubDomains")


def current_request_id() -> str:
    return request_id_var.get()


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        entry = {"ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"), "level": record.levelname,
                 "logger": record.name, "request_id": getattr(record, "request_id", "-"),
                 "message": record.getMessage()}
        for key in ("method", "path", "status", "duration_ms"):
            if hasattr(record, key):
                entry[key] = getattr(record, key)
        if record.exc_info:
            entry["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(entry, ensure_ascii=False)


def configure_logging() -> None:
    handler = logging.StreamHandler()
    handler.addFilter(_RequestIdFilter())
    if settings.log_format == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s [%(request_id)s]: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(settings.log_level)


class RequestContextMiddleware:
    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers") or [])
        incoming = (headers.get(b"x-request-id") or headers.get(b"x-vercel-id") or b"").decode("latin-1")
        request_id = incoming[:128] if incoming else uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        status = 500
        https = scope.get("scheme") == "https" or headers.get(b"x-forwarded-proto") == b"https"

        async def send_wrapper(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                extra = [(b"x-request-id", request_id.encode("latin-1")), *SECURITY_HEADERS]
                if https:
                    extra.append(HSTS)
                message["headers"] = list(message.get("headers") or []) + extra
            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            path = scope.get("path", "")
            if path != "/api/health":  # probes would drown the log
                duration_ms = round((time.perf_counter() - started) * 1000)
                access_log.info("%s %s %s %dms", scope.get("method"), path, status, duration_ms,
                                extra={"method": scope.get("method"), "path": path, "status": status,
                                       "duration_ms": duration_ms})
            request_id_var.reset(token)
