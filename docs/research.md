# Research Notes — TruthLens AI

**Project title:** TruthLens AI — An Explainable Multimodal Information Verification System with Credibility Analytics

**Honesty rule:** These papers are **inspiration**, not systems we claim to reproduce. TruthLens is an integrated **decision-support / credibility-analytics** framework for B.Tech evaluation, not a claimed SOTA reimplementation of MOCHEG/MEVER/etc.

---

## Priority papers (your core Related Work)

| # | Paper | Link | What it contributes | What TruthLens takes | What TruthLens does differently |
|---|--------|------|---------------------|----------------------|----------------------------------|
| 1 | **MOCHEG** — End-to-End Multimodal Fact-Checking and Explanation Generation (Yao et al., SIGIR 2023) | [PDF](https://arxiv.org/pdf/2205.12487) | Multimodal evidence retrieval + verification + explanation; SUPPORT / REFUTE / NEI style labels | Evidence + explanation + multimodal verification pipeline idea | We add **Credibility Analytics**: separate credibility / confidence / risk + action recommendation + analytics/admin product layer |
| 2 | **MEVER** — Multi-Modal and Explainable Claim Verification with Graph-based Evidence Retrieval (Zhang et al., EACL 2026) | [PDF](https://aclanthology.org/2026.eacl-long.242.pdf) | Joint multimodal retrieval + verification + explanation | Explainable multimodal verification with evidence | We do not claim graph neural retrieval; we use practical search/Wikipedia enrichment + backend scoring engines |
| 3 | **RAFTS** — Retrieval Augmented Fact Verification by Synthesizing Contrastive Arguments (Yue et al., ACL 2024) | [PDF](https://aclanthology.org/2024.acl-long.556.pdf) | Retrieval + supporting/refuting arguments + prediction/explanation | Evidence retrieval before LLM judgment; support vs contradict framing | We keep support/contradict evidence types and add deterministic multi-metric scoring + risk/action |
| 4 | **LVLM4FV** — Multimodal Misinformation Detection using Large Vision-Language Models (Tahmasebi et al., 2024) | [PDF](https://arxiv.org/pdf/2407.14321) | Evidence retrieval + LVLM verification (zero-shot) | Multimodal / LLM-era verification with retrieval | Image path in TruthLens uses **OCR→text claim→same pipeline** (not full vision-language claim matching); we state this limit clearly |
| 5 | **FOLK** — Explainable Claim Verification via Knowledge-Grounded Reasoning with LLMs (Wang & Shu, Findings EMNLP 2023) | [PDF](https://aclanthology.org/2023.findings-emnlp.416.pdf) / [page](https://aclanthology.org/2023.findings-emnlp.416/) | Explainable LLM reasoning (FOL-guided) without only black-box labels | Explainable reasoning + structured LLM output | We constrain Gemini to structured JSON over retrieved evidence; final scores/actions are **backend-owned** |

---

## Faculty answer: “Isn’t this just Fake/Real?”

Say:

> Prior systems (MOCHEG, MEVER, RAFTS, FOLK, LVLM4FV) inspire evidence-based multimodal verification and explanation. TruthLens contributes **Credibility Analytics**: instead of collapsing the problem into one Fake/Real label, we separately compute **credibility** (support strength), **confidence** (certainty of conclusion), and **risk** (decision caution), then recommend an action. Gemini is only a structured reasoning stage—not the sole decision-maker.

---

## Gap we claim (for Sem-7 paper)

Many recent works still optimize toward:
- a single veracity label, and/or  
- model-centric confidence,  

with less emphasis on:
1. separating **credibility vs confidence vs risk**,  
2. deterministic, auditable scoring formulas,  
3. operational decision-support (history, analytics, admin monitoring).

TruthLens targets that gap as an **integrated framework** with evaluation planned for Sem-8.

---

## Sem-7 paper use of these papers

**Related Work structure:**
1. Multimodal fact-checking datasets/systems → MOCHEG, MEVER  
2. Retrieval-augmented verification → RAFTS, LVLM4FV  
3. Explainable LLM verification → FOLK, MOCHEG/MEVER explanations  
4. Gap → Credibility Analytics (our work)

**Do not write:** “We implement MOCHEG.”  
**Do write:** “Inspired by MOCHEG’s evidence–verify–explain pipeline, TruthLens …”

---

## Sem-8 evaluation direction (so faculty take the idea seriously)

1. Baseline: Gemini-only Fake/Real vs TruthLens full pipeline  
2. Ablation: with/without evidence enrichment  
3. Metrics: label agreement / F1 on a small labeled set + insufficient-evidence rate + latency  
4. Optional: human rating of explanation usefulness  

---

## Citation starter (informal)

- Yao et al., 2023. MOCHEG. SIGIR. https://arxiv.org/pdf/2205.12487  
- Tahmasebi et al., 2024. LVLM4FV. https://arxiv.org/pdf/2407.14321  
- Zhang et al., 2026. MEVER. EACL. https://aclanthology.org/2026.eacl-long.242.pdf  
- Wang & Shu, 2023. FOLK. Findings of EMNLP. https://aclanthology.org/2023.findings-emnlp.416.pdf  
- Yue et al., 2024. RAFTS. ACL. https://aclanthology.org/2024.acl-long.556.pdf  
