from fastapi import APIRouter

from app.api.routes import ai, batches, media, render, system

api_router = APIRouter(prefix="/api")
for module in (system, ai, render, media, batches):
    api_router.include_router(module.router)
