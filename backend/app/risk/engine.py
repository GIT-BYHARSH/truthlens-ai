"""Risk assessment engine."""

from dataclasses import dataclass

from app.core.enums import RiskLevel, Verdict
from app.scoring.credibility import clamp


@dataclass
class RiskInputs:
    credibility_score: float
    confidence_score: float
    contradiction_intensity: float  # 0-100
    source_reliability: float  # 0-100
    category_sensitivity: float  # 0-100 (health/finance/civic higher)
    verdict: Verdict


def compute_risk(inputs: RiskInputs) -> tuple[float, RiskLevel, str]:
    """
    Higher risk when low credibility is asserted with high confidence,
    contradictions are strong, sources are weak, or topic is sensitive.
    """
    low_cred_pressure = max(0.0, 55.0 - inputs.credibility_score)
    confident_bad = (inputs.confidence_score / 100.0) * low_cred_pressure

    if inputs.verdict in {Verdict.REFUTED, Verdict.INSUFFICIENT_EVIDENCE}:
        verdict_factor = 20.0 if inputs.verdict == Verdict.REFUTED else 12.0
    elif inputs.verdict == Verdict.PARTIALLY_SUPPORTED:
        verdict_factor = 10.0
    elif inputs.verdict == Verdict.UNVERIFIED:
        verdict_factor = 14.0
    else:
        verdict_factor = 4.0

    weak_sources = max(0.0, 60.0 - inputs.source_reliability) * 0.25

    risk = clamp(
        confident_bad * 0.9
        + inputs.contradiction_intensity * 0.25
        + inputs.category_sensitivity * 0.20
        + weak_sources
        + verdict_factor
    )

    if risk >= 80:
        level = RiskLevel.CRITICAL
    elif risk >= 60:
        level = RiskLevel.HIGH
    elif risk >= 35:
        level = RiskLevel.MEDIUM
    else:
        level = RiskLevel.LOW

    rationale = (
        f"Risk {level.value} ({risk:.1f}/100) from credibility/confidence interaction, "
        f"contradiction intensity, source weakness, category sensitivity, and verdict."
    )
    return risk, level, rationale
