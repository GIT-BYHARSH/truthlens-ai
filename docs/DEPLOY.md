# Deploy TruthLens AI (Render + Vercel)

Public stack:
- **Backend API** → [Render](https://render.com) (Docker)
- **Frontend** → [Vercel](https://vercel.com)
- **Database** → [Neon](https://neon.tech) (you already use this)

Repo: https://github.com/GIT-BYHARSH/truthlens-ai

---

## 0) Push deploy files to GitHub first

Commit and push these files (from project root), then continue:

- `backend/Dockerfile`
- `backend/.dockerignore`
- `render.yaml`
- `frontend/vercel.json`
- `frontend/.env.example`
- `docs/DEPLOY.md`

---

## 1) Render — API

1. Open https://dashboard.render.com → **New** → **Blueprint**
2. Connect **GIT-BYHARSH/truthlens-ai** (branch `main`)
3. Apply `render.yaml` → service name `truthlens-api`
4. In **Environment**, set secrets (do not commit these):

| Key | Value |
|-----|--------|
| `DATABASE_URL` | Neon URL with `postgresql+asyncpg://` and `?ssl=require` |
| `GEMINI_API_KEY` | Google AI Studio key |
| `CORS_ORIGINS` | `https://YOUR-APP.vercel.app,http://localhost:5173` (update after Vercel) |

**Neon URL tip:** if Neon gives `postgresql://...`, change to:

```text
postgresql+asyncpg://USER:PASSWORD@HOST/DB?ssl=require
```

5. Deploy. When live, copy the API URL, e.g.:

```text
https://truthlens-api.onrender.com
```

Health check:

```text
https://truthlens-api.onrender.com/api/v1/health
```

### Plan note (important)

`render.yaml` uses **Starter** (~$7/mo) because **EasyOCR + Torch** needs more RAM than free 512MB for reliable image verify.  
Text/URL often work on Free, but image OCR may crash/OOM. Prefer Starter for demos.

Cold start on free/sleeping instances can take 30–90s — wait, then retry.

---

## 2) Vercel — Frontend

1. Open https://vercel.com/new
2. Import **GIT-BYHARSH/truthlens-ai**
3. Configure:

| Setting | Value |
|---------|--------|
| **Root Directory** | `frontend` |
| **Framework** | Vite |
| **Build Command** | `npm run build` |
| **Output Directory** | `dist` |

4. Environment variable (Production + Preview):

| Key | Value |
|-----|--------|
| `VITE_API_BASE` | `https://truthlens-api.onrender.com/api/v1` |

(Use your real Render URL.)

5. Deploy. Copy the frontend URL, e.g.:

```text
https://truthlens-xxxx.vercel.app
```

---

## 3) Wire CORS

Back on Render → `truthlens-api` → Environment → set:

```text
CORS_ORIGINS=https://truthlens-xxxx.vercel.app,http://localhost:5173,http://127.0.0.1:5173
```

Redeploy API (or wait for auto-restart).  
`*.vercel.app` is also allowed by regex in the backend for preview deploys.

---

## 4) Smoke test

1. Open the Vercel URL  
2. Home loads  
3. Verify → text demo claim (Chandrayaan / Mumbai) → report opens  
4. Health: `…onrender.com/api/v1/health` shows `"gemini_configured": true`

---

## 5) Local still works

```powershell
.\start-dev.ps1
```

App: http://127.0.0.1:5173  
Leave `VITE_API_BASE` unset locally so Vite proxies to port 8002.

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Frontend “Cannot reach backend” | Wrong/missing `VITE_API_BASE`; rebuild on Vercel after fixing |
| CORS errors in browser console | Add exact Vercel origin to `CORS_ORIGINS` on Render |
| DB errors | Check `postgresql+asyncpg://` + `ssl=require` |
| Image verify 502 / OOM | Use Render **Starter**; first OCR call is slow |
| API sleeps then timeout | Hit health URL once, wait ~60s, retry Verify |

---

## What you get

| Piece | Public URL |
|-------|------------|
| UI | `https://….vercel.app` |
| API | `https://….onrender.com` |
| API docs | `https://….onrender.com/docs` |
