# TruthLens AI: A Credibility-Analytics Framework for Explainable Multimodal Information Verification

**Authors:** Harsh Kumar Gautam et al.  
**Affiliation:** ABES Engineering College (B.Tech CSE — AI & ML)  
**Status:** Semester-7 draft (framework + pilot plan)  
**Project title (official):** TruthLens AI — An Explainable Multimodal Information Verification System with Credibility Analytics

---

## Abstract

Automated claim verification systems increasingly rely on large language models (LLMs). Many student and industrial demos reduce verification to a single Fake/Real (or support/refute) prediction, conflating *model confidence* with *claim credibility* and omitting decision risk. Inspired by multimodal evidence-based fact-checking research such as MOCHEG, MEVER, RAFTS, LVLM4FV, and FOLK, we present **TruthLens AI**, an explainable multimodal verification framework with **Credibility Analytics**. TruthLens retrieves and ranks evidence before LLM reasoning, constrains Gemini to structured outputs over retrieved evidence, and computes three backend metrics—**credibility**, **confidence**, and **risk**—followed by an action recommendation. Unlike wrapper pipelines, final scores and actions are deterministic and auditable. We describe the architecture, scoring formulation, and a pilot evaluation protocol comparing TruthLens against an LLM-only baseline.

**Keywords:** multimodal fact-checking, credibility analytics, explainable AI, evidence retrieval, LLM, decision support

---

## 1. Introduction

Misinformation and unverified claims motivate automated verification. Recent LLM-based systems can produce fluent judgments, but a common failure mode in academic demos is:

> Input → LLM → Fake/Real

This design is weak for three reasons:
1. It treats the LLM as the sole authority.
2. It collapses support strength and certainty into one score/label.
3. It provides little decision support (what should a user *do*?).

Research systems such as MOCHEG [1] and MEVER [2] emphasize evidence retrieval, multimodal verification, and explanation generation. RAFTS [3] highlights retrieval-augmented verification with supporting/refuting arguments. LVLM4FV [4] studies multimodal evidence with vision-language models. FOLK [5] focuses on explainable LLM reasoning.

**TruthLens contribution.** We integrate these ideas into a practical framework whose primary novelty for undergraduate research is **Credibility Analytics**:
- **Credibility:** how well-supported the claim appears from evidence.
- **Confidence:** how sure the system is about its conclusion.
- **Risk:** decision caution if a user acted on the report.

A claim can be weakly supported (low credibility) while the system is highly sure of that conclusion (high confidence)—e.g., “The capital of India is Mumbai” → REFUTED.

---

## 2. Related Work

### 2.1 Multimodal fact-checking with explanation
MOCHEG [1] proposes end-to-end multimodal fact-checking and explanation generation with evidence retrieval and truthfulness labels (support/refute/not enough information). MEVER [2] jointly addresses multimodal evidence retrieval, verification, and explanation.

### 2.2 Retrieval-augmented and LLM verification
RAFTS [3] retrieves documents and synthesizes contrastive supporting/refuting arguments for verification and explanation. LVLM4FV [4] incorporates evidence retrieval into multimodal misinformation detection using LLMs/LVLMs. FOLK [5] performs explainable claim verification via knowledge-grounded reasoning with LLMs.

### 2.6 Research gap
Despite strong progress, many pipelines still optimize toward a **single veracity decision**. Fewer undergraduate-accessible systems explicitly:
1. separate credibility from confidence and risk,
2. keep scoring formulas deterministic and auditable outside the LLM,
3. expose operational analytics (history, monitoring) as part of verification science.

TruthLens targets this gap.

---

## 3. Proposed Method: Credibility Analytics Framework

### 3.1 Problem formulation
Given claim \(c\) (from text, URL, or OCR text), retrieve evidence set \(E\), predict structured verdict \(v\), and compute:
\[
\text{cred}(c,E),\quad \text{conf}(c,E,v),\quad \text{risk}(c,E,v)
\]
and an action \(a = f(v,\text{risk},\text{conf})\).

### 3.2 Pipeline stages
1. Input validation & claim normalization  
2. Multimodal acquisition (text / URL extract / EasyOCR)  
3. Evidence retrieval & claim-aware ranking  
4. Evidence enrichment (e.g., long Wikipedia extracts)  
5. Gemini structured JSON verification (labels over provided evidence only)  
6. Backend credibility scoring  
7. Backend confidence estimation  
8. Risk assessment  
9. Action recommendation  
10. Persist report + analytics  

### 3.3 Scoring (transparent heuristics)
Credibility aggregates support strength, source reliability, agreement, consistency, minus contradiction/insufficiency penalties.  
Confidence aggregates evidence coverage/quality, weighted model confidence, verdict clarity, minus uncertainty.  
Risk increases when low credibility co-occurs with high certainty, weak sources, or contradictions.

*(Detailed equations in `docs/scoring.md`.)*

### 3.4 LLM role boundary
Gemini may analyze claim–evidence relationships and draft explanation fields.  
Gemini may **not** unilaterally set final credibility, risk, or action without backend rules.

---

## 4. System Implementation

- **Backend:** FastAPI, SQLAlchemy, PostgreSQL  
- **Frontend:** React (Verify, Report, Analytics, Admin, Method)  
- **LLM:** Google Gemini (structured JSON)  
- **OCR:** EasyOCR (text extraction only; not authenticity detection)  
- **Analytics:** Plotly over stored verification events  

---

## 5. Pilot Experiments (Semester 7)

### 5.1 Research questions
- **RQ1:** Does TruthLens disagree with LLM-only Fake/Real style outputs in informative ways?  
- **RQ2:** Does evidence enrichment reduce `INSUFFICIENT_EVIDENCE` on well-documented factual claims?  
- **RQ3:** Can credibility and confidence diverge in expected directions on refuted claims?

### 5.2 Setup
- Pilot claim set: `datasets/pilot/claims.json`  
- Baseline A: Gemini-only (claim → label, no evidence)  
- System B: TruthLens full pipeline  
- Ablation C: TruthLens without snippet enrichment  

### 5.3 Metrics
- Label agreement with gold (SUPPORTED/REFUTED/NEI)  
- Insufficient-evidence rate  
- Average credibility/confidence on correct REFUTED cases (expect low cred, high conf)  
- Latency  

### 5.4 Preliminary pilot results (10 claims)

**Overall (pilot):**

| System | Accuracy | NEI / Insufficient rate | Avg latency |
|--------|----------|--------------------------|-------------|
| Gemini-only (no evidence) | 80% | 20%* | ~2.5 s |
| TruthLens (evidence + scores) | 80% | 20% | ~23 s |

\*Gemini-only “NEI” on c09–c10 includes API quota failures (HTTP 429), not true model abstention.

**Selected case studies (faculty talking points):**

| Claim | Gold | Gemini-only | TruthLens | Credibility Analytics signal |
|-------|--------|-------------|-----------|------------------------------|
| Chandrayaan-3 south pole landing | SUPPORTED | SUPPORTED | SUPPORTED | cred 65.5 / conf 79.5 |
| Capital of India is Mumbai | REFUTED | REFUTED | REFUTED | **cred 20.0 / conf 78.5** |
| WHO COVID pandemic March 2020 | SUPPORTED | SUPPORTED | SUPPORTED | cred 65.8 / conf 79.9 |
| Sun revolves around Earth daily | REFUTED | REFUTED | REFUTED | **cred 18.6 / conf 77.4** |
| Everest entirely in India | REFUTED | REFUTED | REFUTED | **cred 6.3 / conf 72.7** |
| Chandrayaan-2 soft landing success 2019 | REFUTED | (quota fail→NEI) | REFUTED | cred 22.0 / conf 81.0 |

**Interpretation for paper/viva:**
- Accuracy alone looks similar (80% vs 80%) on this tiny set — that is OK for a pilot.
- TruthLens adds **Credibility Analytics**: on REFUTED claims, credibility stays low while confidence stays high.
- This cannot be shown by a Fake/Real wrapper that outputs only one label.
- Full row dump: `datasets/pilot/results_pilot.json`

**Faculty one-liner:**
> Even when both systems say REFUTED, only TruthLens reports low credibility with high confidence — proving multi-metric decision support.

---

## 6. Limitations
- Scoring is heuristic until larger human-labeled evaluation (Sem-8).  
- OCR ≠ deepfake detection.  
- Open-web evidence quality varies.  
- We do not claim reproduction of MOCHEG/MEVER neural architectures.

---

## 7. Conclusion and Future Work
TruthLens reframes undergraduate multimodal verification around **Credibility Analytics** rather than Fake/Real prediction. Semester-8 work will expand labeled evaluation, ablations, and explanation-quality study.

---

## References
[1] Yao et al. End-to-End Multimodal Fact-Checking and Explanation Generation: A Challenging Dataset and Models (MOCHEG). SIGIR 2023. https://arxiv.org/pdf/2205.12487  
[2] Zhang et al. MEVER: Multi-Modal and Explainable Claim Verification with Graph-based Evidence Retrieval. EACL 2026. https://aclanthology.org/2026.eacl-long.242.pdf  
[3] Yue et al. Retrieval Augmented Fact Verification by Synthesizing Contrastive Arguments (RAFTS). ACL 2024. https://aclanthology.org/2024.acl-long.556.pdf  
[4] Tahmasebi et al. Multimodal Misinformation Detection using Large Vision-Language Models (LVLM4FV). 2024. https://arxiv.org/pdf/2407.14321  
[5] Wang & Shu. Explainable Claim Verification via Knowledge-Grounded Reasoning with Large Language Models (FOLK). Findings of EMNLP 2023. https://aclanthology.org/2023.findings-emnlp.416.pdf  
