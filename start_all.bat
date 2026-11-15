@echo off
echo ======================================================================
echo Launching AgriAI Full Stack Platform (FastAPI ML + Next.js Frontend)
echo ======================================================================
cd /d "%~dp0"
start "AgriAI ML Service (Port 8000)" cmd /k "run_ml_service.bat"
timeout /t 3 /nobreak >nul
start "AgriAI Frontend (Port 3000)" cmd /k "run_frontend.bat"
timeout /t 2 /nobreak >nul
start http://localhost:3000
echo.
echo Services launched! Open your browser at http://localhost:3000

