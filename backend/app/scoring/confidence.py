"""Confidence scoring — separate from credibility."""

from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.scoring.credibility import clamp


@dataclass
class ConfidenceInputs:
    evidence_coverage: float  # 0-100
    evidence_quality: float  # 0-100
    model_confidence: float  # 0-100 (Gemini, weighted/capped)
    verdict_clarity: float  # 0-100
    uncertainty_penalty: float  # 0-100


def compute_confidence(
    inputs: ConfidenceInputs,
    settings: Settings | None = None,
) -> tuple[float, str]:
    s = settings or get_settings()
    score = (
        s.confidence_w_coverage * inputs.evidence_coverage
        + s.confidence_w_quality * inputs.evidence_quality
        + s.confidence_w_model * inputs.model_confidence
        + s.confidence_w_clarity * inputs.verdict_clarity
        - s.confidence_w_uncertainty * inputs.uncertainty_penalty
    )
    score = clamp(score)
    rationale = (
        f"Confidence {score:.1f}/100 reflects evidence coverage "
        f"({inputs.evidence_coverage:.0f}), quality ({inputs.evidence_quality:.0f}), "
        f"model signal ({inputs.model_confidence:.0f}), verdict clarity "
        f"({inputs.verdict_clarity:.0f}), minus uncertainty "
        f"({inputs.uncertainty_penalty:.0f})."
    )
    return score, rationale
