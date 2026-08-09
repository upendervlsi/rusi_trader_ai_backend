from fastapi import APIRouter

from backend.services.dashboard_service import DashboardService

router = APIRouter(
    prefix="/api",
    tags=["Dashboard"],
)

service = DashboardService()


@router.get("/dashboard")
def dashboard():

    return service.get_dashboard()
