from backend.app.api.claims import router as claims_router
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.app.api.health import router as health_router
from backend.app.core.config import get_settings
from backend.app.core.logging import configure_logging

configure_logging()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logger.info(
        "Starting %s in %s environment",
        settings.app_name,
        settings.environment,
    )

    yield

    logger.info("Shutting down ClaimLens AI")


settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description="Enterprise Insurance Claim Intelligence Platform",
    version=settings.api_version,
    lifespan=lifespan,
)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "application": settings.app_name,
        "message": "ClaimLens AI API is running",
        "docs": "/docs",
    }

app.include_router(claims_router)
