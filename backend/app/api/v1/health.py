"""Health endpoint."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.schemas.common import HealthOut

router = APIRouter()


@router.get("/health", response_model=HealthOut)
async def health() -> HealthOut:
    settings = get_settings()
    provider = settings.evidence_provider
    if provider == "none":
        provider = "duckduckgo_fallback"
    return HealthOut(
        status="ok",
        app=settings.app_name,
        version="0.2.0",
        evidence_provider=provider,
        gemini_configured=bool(settings.gemini_api_key),
    )
