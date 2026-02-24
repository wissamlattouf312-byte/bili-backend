@echo off
REM BILI: Start backend + frontend locally. Open the link in your browser.
REM Run from: c:\Users\User\Desktop\jona 2\bili

set BILI_ROOT=%~dp0
cd /d "%BILI_ROOT%"

echo.
echo Starting BILI locally...
echo.

REM Start backend in a new window (so it keeps running)
start "BILI Backend" cmd /k "cd /d %BILI_ROOT% && python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend (this will open in current window; when ready, open browser)
echo Starting frontend at http://localhost:3000
echo.
start "BILI Frontend" cmd /k "cd /d %BILI_ROOT%frontend && set BROWSER=none && npm start"

REM Open browser after a short delay (frontend takes ~10-20 sec to compile)
echo.
echo Waiting for frontend to compile (about 15 seconds)...
timeout /t 15 /nobreak > nul
start "" "http://localhost:3000"

echo.
echo ============================================
echo   BILI app should open in your browser.
echo   If not, open this link manually:
echo.
echo   http://localhost:3000
echo.
echo   Or try:  http://127.0.0.1:3000
echo ============================================
pause
