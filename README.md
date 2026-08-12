# TruthLens AI

**Explainable Multimodal Information Verification System with Credibility Analytics**

Final-year B.Tech CSE (AI/ML) major project — an AI-powered **information verification and decision-support platform**, not a simple fake/real classifier.

## What makes this different

| Typical student project | TruthLens AI |
|-------------------------|--------------|
| Input → Gemini → Fake/Real | Full verification pipeline with backend-owned logic |
| Model confidence as “truth” | Separate **Credibility**, **Confidence**, and **Risk** |
| No follow-up | Explainable **action recommendations** |
| One-shot demo | History, analytics insights, admin monitoring |

Gemini is used for structured multimodal reasoning. Evidence retrieval, scoring, risk, and recommendations are deterministic backend components.

## Architecture (high level)

```
User input (text / image / URL)
  → validate → preprocess → OCR (images)
  → claim extraction → evidence retrieval & ranking
  → Gemini structured verification (JSON schema)
  → credibility / confidence / risk / recommendation
  → verification report → PostgreSQL → analytics & admin
```

## Phase status

| Phase | Scope | Status |
|-------|--------|--------|
| 1 | Architecture, DB, API/frontend shells, scoring engines | **Done** |
| 2 | Text + URL verify, Gemini JSON, evidence provider | **Done (core)** |
| 3 | Image + EasyOCR | **Done** |
| 4 | Full scoring wiring in live pipeline | **Done** |
| 5 | History analytics + Plotly / dashboard | Partial (live KPIs) |
| 6 | Hardening, tests, docs polish | Ongoing |

## Quick start

### 1) Prerequisites

- Python 3.12+
- Node.js 20+
- PostgreSQL 16 (Docker Compose **or** free [Neon](https://neon.tech) — Docker is optional)

### 2) Environment

```bash
cp .env.example .env
```

Set at least:

- `DATABASE_URL` — Neon or local Postgres (`postgresql+asyncpg://...`)
- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/)

### 3) Database

**Option A — Docker** (if installed):

```bash
docker compose up -d
```

**Option B — Neon**: create a free project, copy the connection string, change scheme to `postgresql+asyncpg://` and add `?ssl=require` if needed.

### 4) Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --app-dir .
```

API docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/api/v1/health

### 5) Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

### 6) Unit tests (scoring)

```bash
cd backend
pytest ../tests/backend -q
```

## Project structure

```
truthlens-ai/
├── backend/app/     # FastAPI, pipeline, AI, OCR, evidence, scoring, risk, analytics
├── frontend/        # React + Tailwind
├── database/        # SQL migrations
├── docs/            # Pipeline, scoring, research notes
├── datasets/        # Dataset notes (no fabricated data)
├── tests/
├── docker-compose.yml
└── .env.example
```

## Academic honesty

- We do **not** claim to reproduce MOCHEG / LVLM4FV / FEVER systems exactly.
- We do **not** fabricate evidence, scores, analytics, or evaluation results.
- OCR extracts text; it does **not** prove image authenticity.
- The system provides evidence-based decision support, not absolute truth.

See `docs/` for pipeline, scoring formulas, and research gap notes.
