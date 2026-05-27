from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.cash_register import router as cash_register_router
from app.api.v1.catalog import router as catalog_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.expenses import router as expenses_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router
from app.api.v1.sales import router as sales_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(auth_router)
v1_router.include_router(catalog_router)
v1_router.include_router(cash_register_router)
v1_router.include_router(dashboard_router)
v1_router.include_router(expenses_router)
v1_router.include_router(health_router)
v1_router.include_router(reports_router)
v1_router.include_router(sales_router)

__all__ = ["v1_router"]
