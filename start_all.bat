@echo off
echo ========================================
echo Starting Trading Assistant System
echo ========================================
echo.

echo [1/2] Starting backend service...
start "Backend Service" cmd /k "cd /d "%~dp0backend" && python -m uvicorn main:app --host 0.0.0.0 --port 8000"

echo Waiting 3 seconds before starting frontend...
timeout /t 3 /nobreak > nul

echo [2/2] Starting frontend service...
start "Frontend Service" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo ========================================
echo Services started!
echo Backend URL: http://localhost:8000
echo Frontend URL: Check frontend terminal output
echo ========================================
echo.
pause
