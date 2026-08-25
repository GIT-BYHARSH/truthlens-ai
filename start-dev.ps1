# TruthLens AI — start backend (8002) + frontend (5173)
# Usage: from project root, run:  .\start-dev.ps1

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$Python = Join-Path $Backend ".venv\Scripts\python.exe"

Write-Host "TruthLens AI — starting services..." -ForegroundColor Cyan

if (-not (Test-Path $Python)) {
  Write-Host "Missing backend venv. Create it first:" -ForegroundColor Red
  Write-Host "  cd backend; python -m venv .venv; .\.venv\Scripts\activate; pip install -r requirements.txt"
  exit 1
}

if (-not (Test-Path (Join-Path $Frontend "node_modules"))) {
  Write-Host "Installing frontend deps..." -ForegroundColor Yellow
  Push-Location $Frontend
  npm install
  Pop-Location
}

Write-Host "Backend  -> http://127.0.0.1:8002/docs" -ForegroundColor Green
Start-Process powershell -WorkingDirectory $Backend -ArgumentList @(
  "-NoExit",
  "-Command",
  ".\.venv\Scripts\activate; uvicorn app.main:app --reload --app-dir . --host 127.0.0.1 --port 8002"
)

Start-Sleep -Seconds 2

Write-Host "Frontend -> http://127.0.0.1:5173" -ForegroundColor Green
Start-Process powershell -WorkingDirectory $Frontend -ArgumentList @(
  "-NoExit",
  "-Command",
  "npm run dev"
)

Write-Host ""
Write-Host "Open the app at: http://127.0.0.1:5173" -ForegroundColor Cyan
Write-Host "Keep both new terminal windows open while you demo." -ForegroundColor Yellow
