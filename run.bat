@echo off
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
echo ================================================================
echo   QUY NHON SMART TRAVEL - AI Multi-Agent Travel Platform
echo   Powered by Gemini AI + OpenWeatherMap + Google Maps
echo ================================================================
echo.
echo [INFO] Checking API Keys...
if "%GEMINI_API_KEY%"=="" (
    echo [OK] Loading from .env file
)
echo.
echo [INFO] Starting FastAPI server on http://localhost:8000
echo [INFO] Press CTRL+C to stop
echo.
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
pause
