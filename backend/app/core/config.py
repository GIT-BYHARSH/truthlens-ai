"""Central configuration via environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment / .env."""

    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "TruthLens AI"
    app_env: Literal["development", "staging", "production"] = "development"
    debug: bool = True
    api_prefix: str = "/api/v1"
    # Comma-separated string in .env (avoids JSON list parsing issues).
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    database_url: str = (
        "postgresql+asyncpg://truthlens:truthlens@localhost:5432/truthlens"
    )
    create_tables_on_startup: bool = True

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"
    gemini_timeout_seconds: int = 60

    evidence_provider: Literal["none", "serper", "tavily"] = "none"
    serper_api_key: str = ""
    tavily_api_key: str = ""
    evidence_max_results: int = 8

    credibility_w_support: float = 0.30
    credibility_w_source: float = 0.20
    credibility_w_agreement: float = 0.15
    credibility_w_consistency: float = 0.10
    credibility_w_contradiction: float = 0.15
    credibility_w_insufficiency: float = 0.10

    confidence_w_coverage: float = 0.30
    confidence_w_quality: float = 0.25
    confidence_w_model: float = 0.25
    confidence_w_clarity: float = 0.10
    confidence_w_uncertainty: float = 0.10

    upload_dir: str = "uploads"
    max_upload_mb: int = 10

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cors_origin_list(self) -> list[str]:
        return [part.strip() for part in self.cors_origins.split(",") if part.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
