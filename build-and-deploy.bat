@echo off
REM BILI: Build frontend and deploy to https://shiny-choux-bddd03.netlify.app/
REM Run from: c:\Users\User\Desktop\jona 2\bili

set BILI_ROOT=%~dp0
cd /d "%BILI_ROOT%frontend"

echo.
echo [1/2] Building...
call npm run build
if errorlevel 1 (
  echo Build FAILED.
  pause
  exit /b 1
)

echo.
echo [2/2] Deploying to Netlify...
call npx netlify deploy --prod --dir=build
if errorlevel 1 (
  echo Deploy FAILED.
  pause
  exit /b 1
)

echo.
echo Done. Live at https://shiny-choux-bddd03.netlify.app/
pause
