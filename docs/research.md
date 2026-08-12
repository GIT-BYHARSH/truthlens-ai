# Research Notes & Gap

## Inspiration (not reproduction)

Conceptual inspiration from literature related to multimodal fact-checking and explainability, including directions associated with MOCHEG, LVLM4FV, MEVER, FOLK, RAFTS, SpotFake, EANN, dEFEND, EXMULF, and XAI evaluation for fact-checking, plus datasets such as FEVER / FEVEROUS / VERITE where licenses allow.

**We do not claim that TruthLens AI exactly implements any of these systems.**

## Observed limitations in many existing demos

- End at classification (fake/real) without decision support  
- Collapse model confidence into “credibility”  
- Limited evidence ranking + source reliability separation  
- Weak operational analytics / monitoring story for a deployed workflow  

## Our proposed contribution

An **integrated decision-support framework** combining:

1. Multimodal claim verification (text/image/URL)  
2. Evidence retrieval and ranking  
3. Explainable verification reports  
4. Transparent credibility scoring  
5. Separate confidence estimation  
6. Risk assessment  
7. Action recommendation  
8. Verification analytics & admin monitoring  

Primary contribution = **integration + transparent scoring + actionable workflow + evaluation plan**, not an unsupported “novel SOTA algorithm” claim.

## Evaluation plan (later)

- Verification: accuracy / precision / recall / F1 on suitable labeled data  
- Evidence: Precision@K / relevance checks  
- Credibility: consistency vs human ratings where feasible  
- Explainability: clarity / usefulness / completeness / faithfulness (human study)  
- System: latency, OCR success, API failure, evidence success rates  

No fabricated metrics will be published in docs or the UI.
