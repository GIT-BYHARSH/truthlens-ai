"""Evidence ranking helpers."""

from app.core.enums import EvidenceType
from app.evidence.retriever import RawEvidence


def rank_evidence(items: list[RawEvidence]) -> list[RawEvidence]:
    """
    Rank by combined relevance, source reliability, and label strength.
    """

    def sort_key(item: RawEvidence) -> float:
        label_boost = {
            EvidenceType.SUPPORT: 8.0,
            EvidenceType.CONTRADICT: 8.0,
            EvidenceType.NEUTRAL: 0.0,
        }[item.evidence_type]
        return (
            (item.relevance_score or 0.0) * 0.55
            + (item.source_reliability_score or 0.0) * 0.35
            + label_boost
        )

    ranked = sorted(items, key=sort_key, reverse=True)
    return ranked
