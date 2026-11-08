"""Application entrypoint: builds the FastAPI app (API routers + static web UI).

Run locally:  uvicorn app.main:app --reload
Serverless:   api/index.py re-exports `app` (Vercel).
Container:    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers N  (see Dockerfile)
"""
from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.bootstrap import seed
from app.core.observability import RequestContextMiddleware, configure_logging, current_request_id
from app.core.settings import settings

VERSION = "0.4.0"
log = logging.getLogger("agenthub")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Idempotent, lock-protected bootstrap: migrations + demo data; cheap once the database is current.
    await asyncio.to_thread(seed)
    log.info("Enterprise Agent Hub %s ready (database: %s)", VERSION, "sqlite" if settings.is_sqlite else "postgresql")
    yield


async def unhandled_error(request: Request, exc: Exception) -> JSONResponse:
    """Last-resort handler: log the traceback, return a generic message with the correlation id."""
    log.exception("Unhandled error on %s %s", request.method, request.url.path, exc_info=exc)
    return JSONResponse({"detail": "Lỗi hệ thống, vui lòng thử lại.", "request_id": current_request_id()},
                        status_code=500)


def create_app() -> FastAPI:
    configure_logging()
    errors = settings.validate()
    if errors:  # fail fast: a misconfigured instance must not start serving
        raise RuntimeError("Invalid configuration: " + "; ".join(errors))
    for warning in settings.warnings():
        log.warning(warning)

    application = FastAPI(title="Enterprise Agent Hub", version=VERSION, lifespan=lifespan)
    application.add_middleware(RequestContextMiddleware)
    application.add_exception_handler(Exception, unhandled_error)
    application.include_router(api_router)
    application.mount("/static", StaticFiles(directory=settings.static_dir), name="static")

    @application.get("/", include_in_schema=False)
    def index():
        return FileResponse(settings.static_dir / "index.html")

    return application


app = create_app()
