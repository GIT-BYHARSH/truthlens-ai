"""Shared API schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import (
    EvidenceType,
    InputType,
    PipelineStatus,
    RiskLevel,
    Verdict,
)


class EvidenceOut(BaseModel):
    id: UUID
    url: str | None = None
    title: str | None = None
    domain: str | None = None
    evidence_type: EvidenceType
    relevance_score: float | None = None
    snippet: str | None = None
    source_reliability_score: float | None = None
    rank_position: int | None = None

    model_config = {"from_attributes": True}


class ExplanationOut(BaseModel):
    claim_summary: str = ""
    verdict_rationale: str = ""
    key_evidence: list[str] = Field(default_factory=list)
    supporting_points: list[str] = Field(default_factory=list)
    contradicting_points: list[str] = Field(default_factory=list)
    source_reasoning: str = ""
    uncertainties: list[str] = Field(default_factory=list)
    credibility_rationale: str = ""
    confidence_rationale: str = ""
    recommended_action: str = ""


class VerificationReportOut(BaseModel):
    id: UUID
    input_type: InputType
    extracted_text: str | None = None
    claim: str | None = None
    claim_category: str | None = None
    verdict: Verdict | None = None
    credibility_score: float | None = None
    confidence_score: float | None = None
    risk_level: RiskLevel | None = None
    risk_score: float | None = None
    recommendation_code: str | None = None
    recommendation_text: str | None = None
    explanation: ExplanationOut | None = None
    evidence: list[EvidenceOut] = Field(default_factory=list)
    pipeline_status: PipelineStatus
    processing_ms: int | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TextVerifyRequest(BaseModel):
    text: str = Field(..., min_length=8, max_length=8000)
    session_id: str | None = Field(default=None, max_length=64)


class UrlVerifyRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=2048)
    session_id: str | None = Field(default=None, max_length=64)


class HealthOut(BaseModel):
    status: str
    app: str
    version: str
    evidence_provider: str
    gemini_configured: bool


class VerificationListItem(BaseModel):
    id: UUID
    input_type: InputType
    claim: str | None = None
    verdict: Verdict | None = None
    credibility_score: float | None = None
    confidence_score: float | None = None
    risk_level: RiskLevel | None = None
    pipeline_status: PipelineStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class PaginatedVerifications(BaseModel):
    items: list[VerificationListItem]
    total: int
    page: int
    page_size: int


class AnalyticsSummaryOut(BaseModel):
    total_verifications: int
    avg_credibility: float | None
    avg_confidence: float | None
    high_risk_share: float | None
    insufficient_evidence_share: float | None
    verdict_counts: dict[str, int]
    input_type_counts: dict[str, int]
    risk_counts: dict[str, int]


class InsightOut(BaseModel):
    code: str
    message: str


class AdminOverviewOut(BaseModel):
    total_verifications: int
    completed: int
    failed: int
    recent_failures: int
    event_counts: dict[str, int]


class SystemEventOut(BaseModel):
    id: UUID
    event_type: str
    verification_id: UUID | None
    message: str
    created_at: datetime

    model_config = {"from_attributes": True}


class PhaseStubOut(BaseModel):
    """Returned by endpoints not fully implemented in Phase 1."""

    phase: str
    message: str
    status: str = "not_implemented"
