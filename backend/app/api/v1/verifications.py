"""Verification history endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.enums import PipelineStatus
from app.models.verification import Verification
from app.schemas.common import (
    EvidenceOut,
    ExplanationOut,
    PaginatedVerifications,
    VerificationListItem,
    VerificationReportOut,
)

router = APIRouter()


@router.get("", response_model=PaginatedVerifications)
async def list_verifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedVerifications:
    total = await db.scalar(select(func.count()).select_from(Verification)) or 0
    result = await db.execute(
        select(Verification)
        .order_by(Verification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    rows = result.scalars().all()
    items = [
        VerificationListItem(
            id=row.id,
            input_type=row.input_type,  # type: ignore[arg-type]
            claim=row.claim_normalized,
            verdict=row.verdict,  # type: ignore[arg-type]
            credibility_score=row.credibility_score,
            confidence_score=row.confidence_score,
            risk_level=row.risk_level,  # type: ignore[arg-type]
            pipeline_status=PipelineStatus(row.pipeline_status),
            created_at=row.created_at,
        )
        for row in rows
    ]
    return PaginatedVerifications(
        items=items, total=total, page=page, page_size=page_size
    )


@router.get("/{verification_id}", response_model=VerificationReportOut)
async def get_verification(
    verification_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> VerificationReportOut:
    result = await db.execute(
        select(Verification)
        .where(Verification.id == verification_id)
        .options(selectinload(Verification.evidence_items))
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Verification not found")

    explanation = None
    if row.explanation_json:
        explanation = ExplanationOut.model_validate(row.explanation_json)

    return VerificationReportOut(
        id=row.id,
        input_type=row.input_type,  # type: ignore[arg-type]
        extracted_text=row.extracted_text,
        claim=row.claim_normalized,
        claim_category=row.claim_category,
        verdict=row.verdict,  # type: ignore[arg-type]
        credibility_score=row.credibility_score,
        confidence_score=row.confidence_score,
        risk_level=row.risk_level,  # type: ignore[arg-type]
        risk_score=row.risk_score,
        recommendation_code=row.recommendation_code,
        recommendation_text=row.recommendation_text,
        explanation=explanation,
        evidence=[EvidenceOut.model_validate(e) for e in row.evidence_items],
        pipeline_status=PipelineStatus(row.pipeline_status),
        processing_ms=row.processing_ms,
        created_at=row.created_at,
    )
