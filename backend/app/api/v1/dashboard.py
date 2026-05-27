from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_owner_user, get_dashboard_service
from app.domain.user import User
from app.schemas.dashboard import DashboardSummaryResponse
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    _: Annotated[User, Depends(get_current_owner_user)],
    service: Annotated[DashboardService, Depends(get_dashboard_service)],
) -> DashboardSummaryResponse:
    return DashboardSummaryResponse.from_service(service.get_today_summary())
