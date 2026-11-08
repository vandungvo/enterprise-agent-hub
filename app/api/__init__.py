"""HTTP API, one router per domain. `api_router` is mounted by app.main.create_app()."""
from fastapi import APIRouter

from app.api import admin, approvals, audit, chat, health, identity, internal, knowledge, metrics

api_router = APIRouter(prefix="/api")
for module in (health, identity, chat, knowledge, approvals, audit, metrics, admin, internal):
    api_router.include_router(module.router)

__all__ = ["api_router"]
