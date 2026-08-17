# Sem-7 / Sem-8 Research Roadmap

**Project:** TruthLens AI — An Explainable Multimodal Information Verification System with Credibility Analytics

## Goal
Stop faculty from classifying the work as “Fake/Real prediction” by producing:
1. A proper research narrative (paper)
2. Experimental proof (baseline + ablation + metrics)

## Semester plan

### Semester 7 (Paper 1 — Framework paper)
**Working title:**  
*TruthLens AI: A Credibility-Analytics Framework for Explainable Multimodal Information Verification*

**Sections:** Introduction → Related Work (MOCHEG, MEVER, RAFTS, LVLM4FV, FOLK) → Proposed Method → System Implementation → Pilot Experiments → Conclusion  

**Must show:**
- Gap: single-label systems collapse confidence into “truth”
- Contribution: credibility ≠ confidence ≠ risk + action recommendation
- Pilot results on labeled mini-set + case studies

**File:** `docs/paper/sem7_draft.md`

### Semester 8 (Paper 2 — Evaluation paper)
**Working title:**  
*Evaluating Credibility–Confidence–Risk Scoring against LLM-Only Verification Baselines*

**Must show:**
- Larger labeled set / licensed subset
- Gemini-only vs TruthLens comparison table
- Ablation: with/without evidence enrichment
- Metrics: Accuracy/F1, insufficient-evidence rate, latency
- Optional human study on explanations

## Build checklist (this month)
- [ ] Freeze research claim (Credibility Analytics)
- [ ] Finish Sem-7 draft
- [ ] Run pilot evaluation script
- [ ] Put comparison table in paper + PPT
- [ ] Practice one faculty sentence: “Not Fake/Real — multi-metric decision support”

## Commands
```bash
cd backend
.\.venv\Scripts\activate
python -m scripts.eval_pilot
```
