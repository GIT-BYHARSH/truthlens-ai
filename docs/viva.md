# Viva & placement guide — TruthLens AI

## One-line pitch (say this first)

TruthLens AI is an **explainable multimodal information verification system**. It retrieves evidence first, uses Gemini only for structured reasoning, then computes **credibility, confidence, and risk separately**, and returns an **action recommendation** — not a single Fake/Real answer.

## Why this is not “just Gemini”

Faculty rejected Input → AI → Fake/Real. In TruthLens:

| Component | Owner |
|-----------|--------|
| Evidence search + enrichment | Backend |
| Credibility / confidence / risk | Backend formulas |
| Action recommendation | Backend rules |
| Structured claim analysis | Gemini (JSON only, over provided evidence) |

## What makes it unique (memorize 5 points)

1. **Evidence before verdict** — claim-aware ranking + long Wikipedia extracts  
2. **Credibility ≠ Confidence ≠ Risk** — three meters, not one score  
3. **Multimodal** — text / URL / image (EasyOCR extracts text only)  
4. **Decision support** — History, Plotly Analytics, Admin, Print/PDF  
5. **Honest limits** — prefers `INSUFFICIENT_EVIDENCE` over guessing  

## 5-minute demo script (practice aloud)

1. **Home** — brand + “look through evidence, not Fake/Real.”  
2. **Method** — open the interactive three-meter playground; click Credibility → Confidence → Risk; explain Mumbai example.  
3. **Verify** — demo chips in order:  
   - Chandrayaan-3 → **SUPPORTED**  
   - Capital of India is Mumbai → **REFUTED**  
   - WHO pandemic March 2020 → **SUPPORTED**  
4. **Report** — verdict stamp, circular meters, pipeline trace, evidence, Print/PDF.  
5. **Analytics** — show Supported vs Refuted + KPIs (after clean demo).  
6. **Admin** — events; Demo reset if KPIs were polluted by old tests.

### Optional multimodal (OCR) — 1 extra minute

1. **Verify → Image**
2. Upload from `datasets/demo/`:
   - `ocr_supported_chandrayaan.png` → expect **SUPPORTED**
   - or `ocr_refuted_mumbai.png` → expect **REFUTED**
3. On the report, point to **OCR extracted text** and say:  
   “EasyOCR extracts text only — it does not prove the image is authentic.”
4. Then show the same credibility / confidence / risk path as text claims.

## Likely viva Q&A

| Question | Answer |
|----------|--------|
| Why not just Gemini? | Faculty rejected a wrapper. Engines own scores; Gemini only structures reasoning over retrieved evidence. |
| Why low credibility + high confidence? | System can be *sure* a claim is *poorly supported* (e.g. Mumbai capital → REFUTED). |
| Does OCR detect deepfakes? | No — EasyOCR extracts text only; authenticity is out of scope. |
| Is scoring scientific truth? | Transparent heuristics (`docs/scoring.md`), unit-tested; not claimed as validated science. |
| What if evidence is weak? | `INSUFFICIENT_EVIDENCE` + seek-more-evidence action — we do not invent facts. |
| Tech stack? | FastAPI, React, PostgreSQL/Neon, Gemini, EasyOCR, Plotly, Pandas. |

## Worked example (say this on Method)

Claim: “The capital of India is Mumbai.”  
Verdict: **REFUTED**.  
Credibility can be **low** (claim contradicted). Confidence can be **high** (evidence clearly shows New Delhi). Risk rises if someone shared the false claim.

---

## Resume project block (Cease Fire)

**TruthLens AI — Explainable Multimodal Information Verification System**  
*Tech: Python, FastAPI, React, TypeScript, PostgreSQL (Neon), Google Gemini, EasyOCR, Pandas, Plotly*  
*GitHub: https://github.com/GIT-BYHARSH/truthlens-ai*

- Built an end-to-end AI verification platform (text/URL/image) that retrieves evidence before LLM reasoning, then applies deterministic credibility, confidence, and risk engines — not a single Fake/Real label.
- Integrated Google Gemini with strict JSON schemas so the model only labels provided evidence; backend owns scoring, risk, and action recommendations.
- Implemented claim-aware evidence ranking and Wikipedia long-extract enrichment to reduce false “insufficient evidence” on well-documented claims.
- Delivered decision-support UX: explainable reports, printable PDF, Plotly analytics from live Postgres history, and admin monitoring/event streams.

## Short application note

I am applying for the Software Developer role at Cease Fire. My flagship project, TruthLens AI (https://github.com/GIT-BYHARSH/truthlens-ai), is an explainable multimodal information verification system: evidence retrieval + structured Gemini reasoning + separate credibility/confidence/risk engines, with React UI, FastAPI, PostgreSQL analytics, and EasyOCR for images. It maps well to integrating LLMs into real applications, Python/SQL data pipelines, and end-to-end product delivery. I would welcome the chance to discuss how I can contribute to Cease Fire’s AI/software team.
