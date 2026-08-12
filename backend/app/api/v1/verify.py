"""Verification submission endpoints."""

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.database import get_db
from app.core.enums import PipelineStatus
from app.models.verification import Verification
from app.schemas.common import (
    EvidenceOut,
    ExplanationOut,
    TextVerifyRequest,
    UrlVerifyRequest,
    VerificationReportOut,
)
from app.services.pipeline import VerificationPipeline
from app.services.uploads import save_upload_image

router = APIRouter()
pipeline = VerificationPipeline()


def _to_report(row: Verification) -> VerificationReportOut:
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


@router.post("/text", response_model=VerificationReportOut)
async def verify_text(
    body: TextVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationReportOut:
    result = await pipeline.run_text(db, body.text, session_id=body.session_id)
    if result.status != PipelineStatus.COMPLETED or not result.verification_id:
        raise HTTPException(
            status_code=400,
            detail=result.message or "Verification failed",
        )
    row = await _load(db, result.verification_id)
    return _to_report(row)


@router.post("/url", response_model=VerificationReportOut)
async def verify_url(
    body: UrlVerifyRequest,
    db: AsyncSession = Depends(get_db),
) -> VerificationReportOut:
    result = await pipeline.run_url(db, body.url, session_id=body.session_id)
    if result.status != PipelineStatus.COMPLETED or not result.verification_id:
        raise HTTPException(
            status_code=400,
            detail=result.message or "Verification failed",
        )
    row = await _load(db, result.verification_id)
    return _to_report(row)


@router.post("/image", response_model=VerificationReportOut)
async def verify_image(
    file: UploadFile = File(...),
    session_id: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
) -> VerificationReportOut:
    saved = await save_upload_image(file)
    result = await pipeline.run_image(db, str(saved), session_id=session_id)
    if result.status != PipelineStatus.COMPLETED or not result.verification_id:
        raise HTTPException(
            status_code=400,
            detail=result.message or "Image verification failed",
        )
    row = await _load(db, result.verification_id)
    return _to_report(row)


async def _load(db: AsyncSession, verification_id) -> Verification:
    result = await db.execute(
        select(Verification)
        .where(Verification.id == verification_id)
        .options(selectinload(Verification.evidence_items))
    )
    row = result.scalar_one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Verification not found")
    return row
