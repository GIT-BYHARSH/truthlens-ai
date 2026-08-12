# Scoring Formulas (v1)

These formulas are **transparent engineering heuristics** for a decision-support MVP.  
They are **not** claimed as scientifically validated truth measures until evaluated on labeled data.

Scores are on **[0, 100]** unless noted. Weights are configurable via environment variables.

## 1. Credibility (how well-supported the claim appears)

```
credibility =
  w_s * support_strength
+ w_r * source_reliability
+ w_a * cross_source_agreement
+ w_c * claim_consistency
- w_x * contradiction_penalty
- w_i * insufficiency_penalty
```

Default weights: `0.30, 0.20, 0.15, 0.10, 0.15, 0.10`.

**Important:** Credibility is **not** Gemini’s confidence field.

## 2. Confidence (how sure the system is in its conclusion)

```
confidence =
  w_e * evidence_coverage
+ w_q * evidence_quality
+ w_m * model_confidence   # Gemini signal, weighted
+ w_v * verdict_clarity
- w_u * uncertainty_penalty
```

Default weights: `0.30, 0.25, 0.25, 0.10, 0.10`.

Example: Credibility `25`, Confidence `92` → the system is highly sure the claim is poorly supported.

## 3. Risk

Combines low-credibility pressure under high confidence, contradiction intensity, weak sources, category sensitivity, and verdict priors. Mapped to:

| Score | Level |
|------:|-------|
| < 35 | LOW |
| 35–59 | MEDIUM |
| 60–79 | HIGH |
| ≥ 80 | CRITICAL |

Language used in UI: potential decision risk — not proven real-world harm.

## 4. Action recommendation

Deterministic rule matrix on `(verdict × risk × confidence)`, e.g.:

- `REFUTED` + HIGH/CRITICAL → do not rely/share; check official sources  
- `INSUFFICIENT_EVIDENCE` + MEDIUM+ → seek more verification  
- `SUPPORTED` + high confidence + LOW risk → supported; still review citations  

Never recommends illegal or harmful actions.

## Unit tests

See `tests/backend/test_scoring.py` for regression checks on ordering and separation of metrics.
