@echo off
echo ======================================================================
echo Starting AgriAI FastAPI Machine Learning Service on Port 8000
echo ======================================================================
cd /d "%~dp0ml-service"
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
pause

