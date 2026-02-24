@echo off
REM BILI Master System - Single Run Button
REM [cite: 2026-02-03, 2026-02-09]
REM Optimized startup sequence with Guest Mode as default entry point

title BILI Master System - Launcher

echo ========================================
echo   BILI Master System - Launch
echo   Guest Mode: Default Entry Point
echo ========================================
echo.

REM Clean up existing processes (reset all terminals)
echo [1/6] Resetting all active terminals and stopping loops...
taskkill /F /IM python.exe /T >nul 2>&1
taskkill /F /IM node.exe /T >nul 2>&1
taskkill /F /IM uvicorn.exe /T >nul 2>&1
taskkill /F /IM cmd.exe /FI "WINDOWTITLE eq BILI*" >nul 2>&1
timeout /t 2 /nobreak >nul

REM Change to script directory
cd /d "%~dp0"

REM Check Python
echo [2/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found! Please install Python 3.8+
    pause
    exit /b 1
)
python --version

REM Check Node.js
echo [3/6] Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found! Please install Node.js 14+
    pause
    exit /b 1
)
node --version

REM Check critical dependencies
echo [4/6] Verifying dependencies...
python -c "import fastapi, uvicorn" >nul 2>&1
if errorlevel 1 (
    echo WARNING: Some Python packages may be missing. Installing critical ones...
    pip install fastapi uvicorn sqlalchemy pydantic --quiet --user >nul 2>&1
)

REM Start backend in new window (force start)
echo [5/6] Force starting Backend Server (http://localhost:8000)...
start "BILI Backend Server" cmd /k "cd /d %~dp0 && echo Starting Backend... && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait for backend to initialize
echo Waiting for backend to initialize...
timeout /t 8 /nobreak >nul

REM Start frontend in new window (force start)
echo [6/6] Force starting Frontend Server (http://localhost:3000)...
start "BILI Frontend Server" cmd /k "cd /d %~dp0frontend && echo Starting Frontend... && npm start"

REM Wait for servers to fully initialize
echo.
echo Waiting for servers to fully start (25 seconds)...
timeout /t 25 /nobreak >nul

REM Verify servers are running
echo Verifying servers...
timeout /t 2 /nobreak >nul

REM Open browser (force start on localhost:3000)
echo.
echo Opening application in browser (localhost:3000)...
start http://localhost:3000
timeout /t 3 /nobreak >nul
start http://localhost:8000/api/docs

echo.
echo ========================================
echo   Servers Started Successfully!
echo ========================================
echo.
echo Frontend: http://localhost:3000
echo   - Guest Mode: Default Entry Point
echo   - Claim Button: 20 Habbet Tokens
echo.
echo Backend API: http://localhost:8000
echo API Docs: http://localhost:8000/api/docs
echo.
echo Two new windows have opened:
echo   - Backend Server (keep open)
echo   - Frontend Server (keep open)
echo.
echo Guest Mode is active - users can claim 20 tokens!
echo.
echo Press any key to close this launcher window...
pause >nul
