"""Derive scoring inputs from evidence + Gemini output."""

from __future__ import annotations

from app.core.enums import EvidenceType, Verdict
from app.evidence.retriever import RawEvidence, unique_domains
from app.schemas.gemini import GeminiVerificationResult
from app.scoring.confidence import ConfidenceInputs
from app.scoring.credibility import CredibilityInputs


def apply_gemini_labels(
    evidence: list[RawEvidence],
    gemini: GeminiVerificationResult,
) -> list[RawEvidence]:
    by_url = {
        (label.url or "").rstrip("/"): label
        for label in gemini.evidence_labels
        if label.url
    }
    for item in evidence:
        key = (item.url or "").rstrip("/")
        label = by_url.get(key)
        if label is None:
            continue
        item.evidence_type = EvidenceType(label.label)
        item.relevance_score = max(item.relevance_score, label.relevance * 100.0)
    return evidence


def build_credibility_inputs(
    evidence: list[RawEvidence],
    gemini: GeminiVerificationResult,
) -> CredibilityInputs:
    if not evidence:
        return CredibilityInputs(
            support_strength=5.0,
            source_reliability=20.0,
            cross_source_agreement=5.0,
            claim_consistency=20.0,
            contradiction_penalty=10.0,
            insufficiency_penalty=90.0,
        )

    supports = [e for e in evidence if e.evidence_type == EvidenceType.SUPPORT]
    contradicts = [e for e in evidence if e.evidence_type == EvidenceType.CONTRADICT]

    support_strength = _avg([e.relevance_score for e in supports], default=15.0)
    if supports:
        support_strength = min(100.0, support_strength + min(25.0, len(supports) * 6))

    contradiction_penalty = _avg([e.relevance_score for e in contradicts], default=5.0)
    if contradicts:
        contradiction_penalty = min(
            100.0, contradiction_penalty + min(30.0, len(contradicts) * 8)
        )

    source_reliability = _avg(
        [e.source_reliability_score for e in evidence], default=40.0
    )

    domains = unique_domains(evidence)
    agreement = min(100.0, domains * 18.0)
    if supports and contradicts:
        agreement *= 0.55

    consistency = {
        Verdict.SUPPORTED: 80.0,
        Verdict.PARTIALLY_SUPPORTED: 55.0,
        Verdict.REFUTED: 25.0,
        Verdict.UNVERIFIED: 35.0,
        Verdict.INSUFFICIENT_EVIDENCE: 20.0,
    }.get(gemini.verdict, 40.0)

    insufficiency = 0.0
    if len(evidence) < 3:
        insufficiency += 35.0
    if not supports and not contradicts:
        insufficiency += 40.0
    if gemini.verdict == Verdict.INSUFFICIENT_EVIDENCE:
        insufficiency = max(insufficiency, 70.0)

    return CredibilityInputs(
        support_strength=support_strength,
        source_reliability=source_reliability,
        cross_source_agreement=agreement,
        claim_consistency=consistency,
        contradiction_penalty=contradiction_penalty,
        insufficiency_penalty=min(100.0, insufficiency),
    )


def build_confidence_inputs(
    evidence: list[RawEvidence],
    gemini: GeminiVerificationResult,
) -> ConfidenceInputs:
    coverage = min(100.0, len(evidence) * 14.0)
    quality = _avg([e.source_reliability_score for e in evidence], default=25.0)
    model_conf = gemini.model_confidence * 100.0
    clarity = {
        Verdict.SUPPORTED: 85.0,
        Verdict.REFUTED: 85.0,
        Verdict.PARTIALLY_SUPPORTED: 60.0,
        Verdict.UNVERIFIED: 45.0,
        Verdict.INSUFFICIENT_EVIDENCE: 55.0,
    }.get(gemini.verdict, 50.0)
    uncertainty = min(100.0, len(gemini.uncertainties) * 18.0)
    if not evidence:
        uncertainty = max(uncertainty, 70.0)
        coverage = 10.0

    return ConfidenceInputs(
        evidence_coverage=coverage,
        evidence_quality=quality,
        model_confidence=model_conf,
        verdict_clarity=clarity,
        uncertainty_penalty=uncertainty,
    )


def _avg(values: list[float], default: float) -> float:
    nums = [float(v) for v in values if v is not None]
    if not nums:
        return default
    return sum(nums) / len(nums)
