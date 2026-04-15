@echo off
echo ========================================
echo Starting Backend Service...
echo ========================================
cd /d "%~dp0backend"
echo Starting FastAPI backend (port: 8000)
echo.
python -m uvicorn main:app --host 0.0.0.0 --port 8000
pause
