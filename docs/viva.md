# Viva & demo talking points

Use this for faculty evaluation and placement interviews.

## One-line pitch

TruthLens AI is an **explainable multimodal information verification system** that separates **credibility**, **confidence**, and **risk**, retrieves evidence before reasoning, and returns **action recommendations** — not a single Fake/Real Gemini wrapper.

## What makes it unique

1. **Backend-owned decision logic** — scoring, risk, and recommendations are deterministic Python engines; Gemini only emits structured JSON over retrieved evidence.
2. **Metric separation** — credibility ≠ confidence ≠ risk (with a worked Mumbai/New Delhi example on Method).
3. **Evidence enrichment** — claim-aware ranking + long Wikipedia extracts so date/location facts reach the model.
4. **Multimodal path** — text / URL / image (EasyOCR) share one pipeline.
5. **Decision support surface** — History, Plotly Analytics, Admin monitoring, Print/PDF report.

## 5-minute demo script

1. **Home** — brand + “why three metrics.”
2. **Method** — read the worked example aloud.
3. **Verify** — click demo chips in order:
   - Chandrayaan-3 → expect **SUPPORTED**
   - Capital of India is Mumbai → expect **REFUTED**
   - WHO COVID pandemic March 2020 → expect **SUPPORTED**
4. Open a report — show score cards, pipeline trace, evidence, **Print / Save PDF**.
5. **Analytics** — Plotly verdict/risk charts from stored runs.
6. **Admin** — event stream; mention Demo reset for clean KPIs.

## Likely viva questions

| Question | Answer |
|----------|--------|
| Why not just Gemini? | Faculty rejected Input→AI→Fake/Real. Engines own scores; model is a structured reasoner over evidence. |
| Why low credibility + high confidence? | System can be sure a claim is poorly supported. |
| Does OCR prove deepfakes? | No — text extraction only. |
| Is scoring scientific truth? | Transparent heuristics; documented in `docs/scoring.md`; not claimed as validated science. |
| What if evidence is weak? | Prefer `INSUFFICIENT_EVIDENCE` + SEEK_MORE_EVIDENCE. |

## Placement bullets (Cease Fire / SWE)

- Built a FastAPI + React verification platform with evidence retrieval, structured Gemini I/O, and deterministic credibility/confidence/risk engines.
- Designed explainable decision-support UX (reports, Plotly analytics, admin monitoring) instead of a black-box classifier.
- Hardened retrieval (Wikipedia long extracts, claim-aware ranking, retries) to reduce false “insufficient evidence” on well-documented claims.
