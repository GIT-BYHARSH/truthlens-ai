"""Verification event ORM model."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Verification(Base):
    __tablename__ = "verifications"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    input_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    original_input_ref: Mapped[str | None] = mapped_column(Text, nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_normalized: Mapped[str | None] = mapped_column(Text, nullable=True)
    claim_category: Mapped[str | None] = mapped_column(String(64), nullable=True)

    verdict: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    credibility_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    recommendation_code: Mapped[str | None] = mapped_column(String(64), nullable=True)
    recommendation_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    explanation_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    pipeline_status: Mapped[str] = mapped_column(
        String(32), nullable=False, default="pending", index=True
    )
    error_codes: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    processing_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    evidence_items = relationship(
        "EvidenceItem", back_populates="verification", cascade="all, delete-orphan"
    )
    ocr_artifacts = relationship(
        "OcrArtifact", back_populates="verification", cascade="all, delete-orphan"
    )
