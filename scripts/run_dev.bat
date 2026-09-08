@echo off
title AI-Livestock Health Sentinel - Dev Server
echo ========================================================
echo Starting AI-Livestock Health Sentinel Development Servers
echo ========================================================

cd /d "%~dp0.."

echo Starting FastAPI backend on http://localhost:8000 ...
start "Sentinel Backend" cmd /k "cd backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

echo Starting Vite frontend on http://localhost:5173 ...
start "Sentinel Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are launching in dedicated console windows.
echo Frontend: http://localhost:5173
echo Backend API docs: http://localhost:8000/docs
echo ========================================================
pause
