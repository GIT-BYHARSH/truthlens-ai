"""Aggregate v1 API router."""

from fastapi import APIRouter

from app.api.v1 import admin, analytics, health, verifications, verify

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(verify.router, prefix="/verify", tags=["verify"])
api_router.include_router(
    verifications.router, prefix="/verifications", tags=["verifications"]
)
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
