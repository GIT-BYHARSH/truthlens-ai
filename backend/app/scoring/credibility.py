"""Credibility scoring — deterministic backend formula (not Gemini confidence)."""

from dataclasses import dataclass

from app.core.config import Settings, get_settings


@dataclass
class CredibilityInputs:
    support_strength: float  # 0-100
    source_reliability: float  # 0-100
    cross_source_agreement: float  # 0-100
    claim_consistency: float  # 0-100
    contradiction_penalty: float  # 0-100
    insufficiency_penalty: float  # 0-100


def clamp(value: float, low: float = 0.0, high: float = 100.0) -> float:
    return max(low, min(high, value))


def compute_credibility(
    inputs: CredibilityInputs,
    settings: Settings | None = None,
) -> tuple[float, str]:
    """
    Credibility = weighted support/source/agreement/consistency
                  minus contradiction and insufficiency penalties.
    """
    s = settings or get_settings()
    score = (
        s.credibility_w_support * inputs.support_strength
        + s.credibility_w_source * inputs.source_reliability
        + s.credibility_w_agreement * inputs.cross_source_agreement
        + s.credibility_w_consistency * inputs.claim_consistency
        - s.credibility_w_contradiction * inputs.contradiction_penalty
        - s.credibility_w_insufficiency * inputs.insufficiency_penalty
    )
    score = clamp(score)
    rationale = (
        f"Credibility {score:.1f}/100 from support ({inputs.support_strength:.0f}), "
        f"source reliability ({inputs.source_reliability:.0f}), agreement "
        f"({inputs.cross_source_agreement:.0f}), consistency "
        f"({inputs.claim_consistency:.0f}), minus contradiction "
        f"({inputs.contradiction_penalty:.0f}) and insufficiency "
        f"({inputs.insufficiency_penalty:.0f}) penalties."
    )
    return score, rationale
