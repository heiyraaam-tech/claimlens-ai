from fastapi import APIRouter

from backend.app.core.config import get_settings
from backend.app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live", response_model=HealthResponse)
def liveness_check():
    settings = get_settings()

    return HealthResponse(
        status="alive",
        application=settings.app_name,
        environment=settings.environment,
    )


@router.get("/ready", response_model=HealthResponse)
def readiness_check():
    settings = get_settings()

    return HealthResponse(
        status="ready",
        application=settings.app_name,
        environment=settings.environment,
    )
