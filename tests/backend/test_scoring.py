from app.recommendations.engine import recommend_action
from app.risk.engine import RiskInputs, compute_risk
from app.scoring.confidence import ConfidenceInputs, compute_confidence
from app.scoring.credibility import CredibilityInputs, compute_credibility
from app.core.enums import RiskLevel, Verdict


def test_credibility_penalizes_contradiction():
    high, _ = compute_credibility(
        CredibilityInputs(80, 80, 70, 70, contradiction_penalty=10, insufficiency_penalty=5)
    )
    low, _ = compute_credibility(
        CredibilityInputs(80, 80, 70, 70, contradiction_penalty=90, insufficiency_penalty=5)
    )
    assert high > low


def test_confidence_distinct_from_credibility_semantics():
    # System can be confident that something is weakly supported.
    conf, _ = compute_confidence(
        ConfidenceInputs(90, 85, 80, 90, uncertainty_penalty=5)
    )
    cred, _ = compute_credibility(
        CredibilityInputs(20, 30, 20, 25, contradiction_penalty=70, insufficiency_penalty=40)
    )
    assert conf > 70
    assert cred < 40


def test_risk_refuted_high():
    score, level, _ = compute_risk(
        RiskInputs(
            credibility_score=15,
            confidence_score=90,
            contradiction_intensity=80,
            source_reliability=40,
            category_sensitivity=50,
            verdict=Verdict.REFUTED,
        )
    )
    assert score >= 60
    assert level in {RiskLevel.HIGH, RiskLevel.CRITICAL}


def test_recommendation_refuted_critical():
    rec = recommend_action(Verdict.REFUTED, RiskLevel.CRITICAL, 90)
    assert rec.code == "DO_NOT_RELY"
