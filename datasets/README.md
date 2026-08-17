# Datasets

Do not place fabricated labeled datasets here to “prove” accuracy.

## OCR demo images (for multimodal viva)

Folder: `datasets/demo/`

| File | Expected outcome |
|------|------------------|
| `ocr_supported_chandrayaan.png` | SUPPORTED |
| `ocr_refuted_mumbai.png` | REFUTED |

### How to demo

1. Open **Verify → Image**
2. Upload one of the PNGs above
3. Wait for EasyOCR (first run may download models)
4. On the report, show **OCR extracted text** + disclaimer: OCR does **not** prove authenticity
5. Then show verdict / scores / evidence as usual

These images were created locally for smoke/demo only — not a benchmark dataset.

## Evaluation datasets (later)

Before any evaluation experiments:

1. Review license and redistribution terms  
2. Document format, labels, and split protocol  
3. Cite the original paper/source  

Candidate families: FEVER / FEVEROUS, VERITE, and literature-review resources (e.g. MOCHEG-related).

## Pilot evaluation set (Sem-7)

- Folder: `datasets/pilot/`
- `claims.json` — 10 labeled claims (SUPPORTED/REFUTED) for baseline comparison
- Run from `backend/`: `python -m scripts.eval_pilot`
- Output: `datasets/pilot/results_pilot.json`

This is a **pilot**, not FEVER-scale evaluation. Use it in the Sem-7 paper to contrast Gemini-only vs TruthLens.
