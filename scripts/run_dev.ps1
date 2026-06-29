param(
  [string]$BackendHost = "127.0.0.1",
  [int]$BackendPort = 8000,
  [int]$FrontendPort = 5173
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"
$VenvPython = Join-Path $Backend ".venv\Scripts\python.exe"

Write-Host "Checking FFmpeg..."
if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
  Write-Host "FFmpeg is missing. Install it and make sure ffmpeg is on PATH."
  exit 1
}
if (-not (Get-Command ffprobe -ErrorAction SilentlyContinue)) {
  Write-Host "ffprobe is missing. Install FFmpeg full build and make sure ffprobe is on PATH."
  exit 1
}

if (-not (Test-Path $VenvPython)) {
  Write-Host "Backend virtual environment not found."
  Write-Host "Create it with:"
  Write-Host "  cd `"$Backend`""
  Write-Host "  py -3.11 -m venv .venv"
  Write-Host "  .\.venv\Scripts\python -m pip install -r requirements-dev.txt"
  exit 1
}

Write-Host "Starting FastAPI and Vite. Close the opened terminals to stop servers."
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", "cd `"$Backend`"; .\.venv\Scripts\python -m uvicorn app.main:app --reload --host $BackendHost --port $BackendPort"
Start-Process powershell -WindowStyle Normal -ArgumentList "-NoExit", "-Command", "cd `"$Frontend`"; npm.cmd run dev -- --host 127.0.0.1 --port $FrontendPort"

