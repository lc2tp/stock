@echo off
echo ========================================
echo Starting Frontend Service...
echo ========================================
cd /d "%~dp0frontend"
echo Starting Vite frontend dev server
echo.
npm run dev
pause
