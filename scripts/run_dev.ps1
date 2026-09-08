# PowerShell script to launch both backend and frontend dev servers
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootDir = Split-Path -Parent $scriptDir

Write-Host "========================================================" -ForegroundColor Green
Write-Host "Starting AI-Livestock Health Sentinel Development Servers" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Green

# 1. Start Backend in separate window
Write-Host "Launching FastAPI Backend on http://localhost:8000 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\backend'; uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start Frontend in separate window
Write-Host "Launching React Vite Frontend on http://localhost:5173 ..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$rootDir\frontend'; npm run dev"

Write-Host "Development environment launched successfully!" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Yellow
Write-Host "Backend API Docs: http://localhost:8000/docs" -ForegroundColor Yellow
