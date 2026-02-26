"""
Dashboard API route.
"""

from fastapi import APIRouter

from app.core.dependencies import CurrentUser, DbDep
from app.schemas.common import BaseResponse
from app.schemas.dashboard import DashboardStats
from app.services.dashboard import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=BaseResponse[DashboardStats])
def get_stats(db: DbDep, _user: CurrentUser):
    """Get aggregated dashboard statistics."""
    service = DashboardService(db)
    stats = service.get_stats()
    return BaseResponse.ok(stats)
