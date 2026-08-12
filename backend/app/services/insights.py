"""Data-driven insight strings — never fabricate when data is insufficient."""

from app.core.enums import RiskLevel, Verdict
from app.schemas.common import AnalyticsSummaryOut, InsightOut


def build_insights(summary: AnalyticsSummaryOut) -> list[InsightOut]:
    if summary.total_verifications == 0:
        return [
            InsightOut(
                code="NO_DATA",
                message=(
                    "No verification history yet. Insights will appear after "
                    "real verification events are stored."
                ),
            )
        ]

    insights: list[InsightOut] = []
    total = summary.total_verifications

    if summary.input_type_counts:
        top_input, top_count = max(
            summary.input_type_counts.items(), key=lambda item: item[1]
        )
        insights.append(
            InsightOut(
                code="TOP_INPUT",
                message=(
                    f"{top_input.upper()}-based verification is the most common "
                    f"input type ({top_count}/{total})."
                ),
            )
        )

    if summary.verdict_counts:
        top_verdict, top_vcount = max(
            summary.verdict_counts.items(), key=lambda item: item[1]
        )
        insights.append(
            InsightOut(
                code="TOP_VERDICT",
                message=(
                    f"Most verification cases currently fall into the "
                    f"{top_verdict} category ({top_vcount}/{total})."
                ),
            )
        )

    insuff = summary.verdict_counts.get(Verdict.INSUFFICIENT_EVIDENCE, 0)
    if insuff / total >= 0.35:
        insights.append(
            InsightOut(
                code="INSUFFICIENT_SHARE",
                message=(
                    "A substantial share of cases have insufficient evidence, "
                    "highlighting the need for careful action recommendations."
                ),
            )
        )

    high = summary.risk_counts.get(RiskLevel.HIGH, 0) + summary.risk_counts.get(
        RiskLevel.CRITICAL, 0
    )
    if high / total >= 0.25:
        insights.append(
            InsightOut(
                code="HIGH_RISK_SHARE",
                message=(
                    "High/critical risk outcomes represent a notable portion of "
                    "stored verifications in the current dataset."
                ),
            )
        )

    if summary.avg_credibility is not None and summary.avg_confidence is not None:
        insights.append(
            InsightOut(
                code="SCORE_MEANS",
                message=(
                    f"Average credibility is {summary.avg_credibility:.1f}/100 and "
                    f"average confidence is {summary.avg_confidence:.1f}/100 "
                    "(these metrics measure different things)."
                ),
            )
        )

    if summary.category_counts:
        top_cat, top_ccount = max(
            summary.category_counts.items(), key=lambda item: item[1]
        )
        insights.append(
            InsightOut(
                code="TOP_CATEGORY",
                message=(
                    f"Most claims are currently categorized as {top_cat} "
                    f"({top_ccount}/{total})."
                ),
            )
        )

    return insights
