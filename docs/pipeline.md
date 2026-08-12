# Verification Pipeline

TruthLens AI runs an ordered pipeline. Stages must not be collapsed into a single “is this fake?” Gemini prompt.

## Stages

1. **Input validation** — type, size, empty/malformed checks  
2. **Content preprocessing** — normalize whitespace/encoding; store input metadata  
3. **OCR / text extraction** — EasyOCR for images; fetch+extract for URLs  
4. **Claim extraction & normalization** — structured claim text (+ optional category)  
5. **Evidence retrieval** — external search/fetch via pluggable provider  
6. **Evidence cleaning & ranking** — relevance, domain independence, dedupe  
7. **Multimodal verification** — Gemini returns **strict JSON** only  
8. **Contradiction / support analysis** — classify evidence roles  
9. **Explainable reasoning** — auditable summary fields (no hidden CoT dump)  
10. **Credibility scoring** — backend weighted formula  
11. **Confidence estimation** — separate from credibility  
12. **Risk assessment** — LOW → CRITICAL  
13. **Action recommendation** — explainable rule matrix  
14. **Verification report** — structured response for UI/export  
15. **PostgreSQL storage** — verification + evidence + OCR artifacts + events  
16. **Analytics & monitoring** — KPIs, insights, admin failure views  

## Gemini role

Allowed: claim analysis, evidence interpretation, structured verdict fields, explanation drafts.  

Not allowed as sole authority: final credibility score, source trust label, risk level, or action recommendation without backend rules.

All model JSON is validated with Pydantic before use. On failure → graceful `INSUFFICIENT_EVIDENCE` / pipeline error event.
