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
| 5 | History analytics + Plotly / dashboard | **Done** |
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
uvicorn app.main:app --reload --app-dir . --host 127.0.0.1 --port 8002
```

API docs: http://127.0.0.1:8002/docs  
Health: http://127.0.0.1:8002/api/v1/health

> On Windows, always use **8002** (port 8000 is often blocked). The Vite proxy targets 8002.

**One-click local run (Windows):** from the project root:

```powershell
.\start-dev.ps1
```

Then open **http://127.0.0.1:5173** (keep both new terminals open).

### 5) Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

Image verify needs the backend running. First EasyOCR call can take 1–2 minutes while models load.

### 6) Unit tests (scoring)

```bash
cd backend
pytest ../tests/backend -q
```

### 7) Public deploy (Render + Vercel)

Step-by-step: [`docs/DEPLOY.md`](docs/DEPLOY.md)

- Backend Docker → Render (`truthlens-api`)
- Frontend → Vercel (root `frontend`, set `VITE_API_BASE`)
- Database → Neon (`postgresql+asyncpg://…?ssl=require`)

## 5-minute viva demo

1. Open **Method** — explain credibility ≠ confidence ≠ risk (worked Mumbai example).
2. **Verify** → use the three demo chips:
   - Chandrayaan-3 landing → **SUPPORTED**
   - Capital of India is Mumbai → **REFUTED**
   - WHO COVID pandemic March 2020 → **SUPPORTED**
3. On the report: pipeline trace, evidence, **Print / Save PDF**.
4. **Analytics** — Plotly charts from stored runs.
5. **Admin** — events; optional **Demo reset** then re-run the three claims for clean KPIs.

Full talking points: [`docs/viva.md`](docs/viva.md)

## Project structure

```
truthlens-ai/
├── backend/app/     # FastAPI, pipeline, AI, OCR, evidence, scoring, risk, analytics
├── backend/Dockerfile
├── frontend/        # React + Tailwind (+ vercel.json)
├── database/        # SQL migrations
├── docs/            # Pipeline, scoring, research, DEPLOY.md
├── datasets/        # Dataset notes (no fabricated data)
├── tests/
├── render.yaml      # Render Blueprint
├── start-dev.ps1    # Local Windows start
├── docker-compose.yml
└── .env.example
```

## Academic honesty

- We do **not** claim to reproduce MOCHEG / LVLM4FV / FEVER systems exactly.
- We do **not** fabricate evidence, scores, analytics, or evaluation results.
- OCR extracts text; it does **not** prove image authenticity.
- The system provides evidence-based decision support, not absolute truth.

See `docs/` for pipeline, scoring formulas, and research gap notes.
