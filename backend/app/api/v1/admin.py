"""Admin monitoring endpoints."""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enums import PipelineStatus
from app.models.evidence import EvidenceItem
from app.models.ocr import OcrArtifact
from app.models.system_event import SystemEvent
from app.models.verification import Verification
from app.schemas.common import AdminOverviewOut, DemoResetOut, SystemEventOut

router = APIRouter()


@router.get("/overview", response_model=AdminOverviewOut)
async def admin_overview(db: AsyncSession = Depends(get_db)) -> AdminOverviewOut:
    total = await db.scalar(select(func.count()).select_from(Verification)) or 0
    completed = await db.scalar(
        select(func.count()).where(
            Verification.pipeline_status == PipelineStatus.COMPLETED
        )
    ) or 0
    failed = await db.scalar(
        select(func.count()).where(
            Verification.pipeline_status == PipelineStatus.FAILED
        )
    ) or 0

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    recent_failures = await db.scalar(
        select(func.count()).where(
            Verification.pipeline_status == PipelineStatus.FAILED,
            Verification.created_at >= since,
        )
    ) or 0

    event_rows = await db.execute(
        select(SystemEvent.event_type, func.count()).group_by(SystemEvent.event_type)
    )
    event_counts = {str(t): c for t, c in event_rows.all()}

    return AdminOverviewOut(
        total_verifications=total,
        completed=completed,
        failed=failed,
        recent_failures=recent_failures,
        event_counts=event_counts,
    )


@router.get("/events", response_model=list[SystemEventOut])
async def admin_events(
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[SystemEventOut]:
    result = await db.execute(
        select(SystemEvent).order_by(SystemEvent.created_at.desc()).limit(limit)
    )
    return [SystemEventOut.model_validate(e) for e in result.scalars().all()]


@router.post("/demo-reset", response_model=DemoResetOut)
async def admin_demo_reset(
    confirm: bool = Query(False),
    db: AsyncSession = Depends(get_db),
) -> DemoResetOut:
    """
    Clear verification history for a clean viva/demo Analytics view.
    Deletes evidence/OCR via FK cascade; system events keep messages with NULL verification_id.
    """
    if not confirm:
        return DemoResetOut(
            deleted_verifications=0,
            message="Pass confirm=true to delete all verifications.",
        )

    count = await db.scalar(select(func.count()).select_from(Verification)) or 0
    # Explicit child deletes for drivers that don't honor ORM cascade on bulk delete.
    await db.execute(EvidenceItem.__table__.delete())
    await db.execute(OcrArtifact.__table__.delete())
    await db.execute(Verification.__table__.delete())
    await db.commit()
    return DemoResetOut(
        deleted_verifications=count,
        message=f"Deleted {count} verification(s). Re-run the 3 demo claims before Analytics.",
    )
