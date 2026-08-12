"""TruthLens AI FastAPI application entrypoint."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.database import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Startup/shutdown hooks."""
    settings = get_settings()
    if settings.create_tables_on_startup:
        try:
            await init_db()
        except Exception as exc:  # noqa: BLE001 - surface clearly in early MVP
            print(
                f"[TruthLens] Database init skipped/failed: {exc}. "
                "API will start; DB-backed routes need PostgreSQL (Neon or Docker)."
            )
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        description=(
            "Explainable multimodal information verification with credibility "
            "analytics and decision-support recommendations."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.include_router(api_router, prefix=settings.api_prefix)
    return application


app = create_app()
