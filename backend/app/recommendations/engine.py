"""Explainable action recommendation rules."""

from dataclasses import dataclass

from app.core.enums import RiskLevel, Verdict


@dataclass
class Recommendation:
    code: str
    text: str
    rationale: str


def recommend_action(
    verdict: Verdict,
    risk: RiskLevel,
    confidence: float,
) -> Recommendation:
    """Rule matrix — never suggests illegal or harmful actions."""

    if verdict == Verdict.REFUTED and risk in {RiskLevel.HIGH, RiskLevel.CRITICAL}:
        return Recommendation(
            code="DO_NOT_RELY",
            text=(
                "Do not rely on or share this information. Cross-check using an "
                "official or primary source before any decision."
            ),
            rationale="Refuted claim with elevated risk.",
        )

    if verdict == Verdict.INSUFFICIENT_EVIDENCE and risk in {
        RiskLevel.MEDIUM,
        RiskLevel.HIGH,
        RiskLevel.CRITICAL,
    }:
        return Recommendation(
            code="SEEK_MORE_EVIDENCE",
            text=(
                "Additional verification is recommended before making a decision. "
                "Available evidence is insufficient for a reliable conclusion."
            ),
            rationale="Insufficient evidence with non-low risk.",
        )

    if verdict == Verdict.SUPPORTED and confidence >= 70 and risk == RiskLevel.LOW:
        return Recommendation(
            code="REVIEW_SOURCES",
            text=(
                "Information is supported by the available evidence. Review the "
                "cited sources and retain normal caution before acting."
            ),
            rationale="Supported with relatively high confidence and low risk.",
        )

    if verdict == Verdict.PARTIALLY_SUPPORTED:
        return Recommendation(
            code="VERIFY_CONTESTED_PARTS",
            text=(
                "Treat this claim as only partially supported. Verify contested "
                "details independently before relying on the full statement."
            ),
            rationale="Partial support requires targeted follow-up.",
        )

    if verdict == Verdict.UNVERIFIED:
        return Recommendation(
            code="DO_NOT_ACT_YET",
            text=(
                "The claim remains unverified. Do not treat it as established fact "
                "until stronger evidence is available."
            ),
            rationale="Unverified verdict.",
        )

    return Recommendation(
        code="PROCEED_WITH_CAUTION",
        text=(
            "Use caution. Review the evidence, source reliability, and explanation "
            "before drawing conclusions or sharing."
        ),
        rationale="Default cautious recommendation.",
    )
