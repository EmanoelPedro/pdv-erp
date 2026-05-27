from fastapi import APIRouter

from app.api.v1 import v1_router
from app.api.v1.health import root_health_router

api_router = APIRouter()
api_router.include_router(root_health_router)
api_router.include_router(v1_router, prefix="/api")
