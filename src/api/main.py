from fastapi import FastAPI

from api.routers.telemetry import router as telemetry_router
from api.core.api_settings import get_api_settings
from api.core.lifespan import lifespan

settings = get_api_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.include_router(telemetry_router, prefix=settings.api_prefix)
