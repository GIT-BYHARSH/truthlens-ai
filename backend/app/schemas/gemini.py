"""Pydantic schemas for Gemini structured verification output."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from app.core.enums import Verdict


class EvidenceLabel(BaseModel):
    url: str | None = None
    title: str | None = None
    label: Literal["support", "contradict", "neutral"] = "neutral"
    relevance: float = Field(default=0.5, ge=0.0, le=1.0)
    rationale: str = ""


class GeminiVerificationResult(BaseModel):
    """Strict schema — validate before any scoring/persistence."""

    claim_normalized: str = Field(..., min_length=3)
    claim_category: str = "general"
    verdict: Verdict
    model_confidence: float = Field(..., ge=0.0, le=1.0)
    claim_summary: str = ""
    reasoning_summary: str = ""
    supporting_points: list[str] = Field(default_factory=list)
    contradicting_points: list[str] = Field(default_factory=list)
    uncertainties: list[str] = Field(default_factory=list)
    evidence_labels: list[EvidenceLabel] = Field(default_factory=list)
    category_sensitivity: float = Field(
        default=30.0,
        ge=0.0,
        le=100.0,
        description="Topic sensitivity prior for risk (health/finance/civic higher).",
    )

    @field_validator("claim_category")
    @classmethod
    def normalize_category(cls, value: str) -> str:
        cleaned = (value or "general").strip().lower()
        allowed = {
            "general",
            "health",
            "finance",
            "civic",
            "tech",
            "science",
            "other",
        }
        return cleaned if cleaned in allowed else "other"
