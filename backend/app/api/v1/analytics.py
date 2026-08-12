"""Analytics endpoints — real aggregates from PostgreSQL only."""

from fastapi import APIRouter, Depends
from sqlalchemy import Float, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.enums import RiskLevel, Verdict
from app.models.verification import Verification
from app.schemas.common import (
    AnalyticsSummaryOut,
    AnalyticsTrendsOut,
    InsightOut,
    TrendPointOut,
)
from app.services.insights import build_insights

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummaryOut)
async def analytics_summary(db: AsyncSession = Depends(get_db)) -> AnalyticsSummaryOut:
    total = await db.scalar(select(func.count()).select_from(Verification)) or 0
    avg_cred = await db.scalar(select(func.avg(Verification.credibility_score)))
    avg_conf = await db.scalar(select(func.avg(Verification.confidence_score)))

    verdict_rows = await db.execute(
        select(Verification.verdict, func.count()).group_by(Verification.verdict)
    )
    verdict_counts = {str(v or "UNKNOWN"): c for v, c in verdict_rows.all()}

    input_rows = await db.execute(
        select(Verification.input_type, func.count()).group_by(Verification.input_type)
    )
    input_type_counts = {str(i): c for i, c in input_rows.all()}

    risk_rows = await db.execute(
        select(Verification.risk_level, func.count()).group_by(Verification.risk_level)
    )
    risk_counts = {str(r or "UNKNOWN"): c for r, c in risk_rows.all()}

    category_rows = await db.execute(
        select(Verification.claim_category, func.count()).group_by(
            Verification.claim_category
        )
    )
    category_counts = {
        str(cat or "uncategorized"): count for cat, count in category_rows.all()
    }

    high_risk = risk_counts.get(RiskLevel.HIGH, 0) + risk_counts.get(
        RiskLevel.CRITICAL, 0
    )
    insuff = verdict_counts.get(Verdict.INSUFFICIENT_EVIDENCE, 0)

    return AnalyticsSummaryOut(
        total_verifications=total,
        avg_credibility=float(avg_cred) if avg_cred is not None else None,
        avg_confidence=float(avg_conf) if avg_conf is not None else None,
        high_risk_share=(high_risk / total) if total else None,
        insufficient_evidence_share=(insuff / total) if total else None,
        verdict_counts=verdict_counts,
        input_type_counts=input_type_counts,
        risk_counts=risk_counts,
        category_counts=category_counts,
    )


@router.get("/insights", response_model=list[InsightOut])
async def analytics_insights(db: AsyncSession = Depends(get_db)) -> list[InsightOut]:
    summary = await analytics_summary(db)
    return build_insights(summary)


@router.get("/trends", response_model=AnalyticsTrendsOut)
async def analytics_trends(db: AsyncSession = Depends(get_db)) -> AnalyticsTrendsOut:
    """Daily verification counts from stored data (empty until verifications exist)."""
    rows = await db.execute(
        select(
            func.date_trunc("day", Verification.created_at).label("day"),
            func.count().label("count"),
            cast(func.avg(Verification.credibility_score), Float).label(
                "avg_credibility"
            ),
            cast(func.avg(Verification.confidence_score), Float).label(
                "avg_confidence"
            ),
        )
        .group_by("day")
        .order_by("day")
    )
    points = [
        TrendPointOut(
            day=day.isoformat() if day else None,
            count=count,
            avg_credibility=avg_credibility,
            avg_confidence=avg_confidence,
        )
        for day, count, avg_credibility, avg_confidence in rows.all()
    ]
    return AnalyticsTrendsOut(points=points)
