# BILI Master System - Single Run Script
# [cite: 2026-02-09]
# This script starts both backend and frontend servers

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BILI Master System - Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Clean up any existing processes
Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow
Get-Process | Where-Object {$_.ProcessName -match "python|node|uvicorn|npm"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Set working directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

# Check Python
Write-Host "Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Python not found!" -ForegroundColor Red
    exit 1
}

# Check Node.js
Write-Host "Checking Node.js..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ERROR: Node.js not found!" -ForegroundColor Red
    exit 1
}

# Install critical Python dependencies if missing
Write-Host ""
Write-Host "Checking Python dependencies..." -ForegroundColor Yellow
$testImport = python -c "import fastapi, uvicorn, sqlalchemy" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "  Installing critical dependencies..." -ForegroundColor Yellow
    pip install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-dotenv --quiet --user 2>&1 | Out-Null
}

# Check frontend dependencies
Write-Host "Checking frontend dependencies..." -ForegroundColor Yellow
if (-not (Test-Path "frontend\node_modules")) {
    Write-Host "  Installing frontend dependencies (this may take a minute)..." -ForegroundColor Yellow
    Set-Location frontend
    npm install --silent 2>&1 | Out-Null
    Set-Location ..
}

Write-Host ""
Write-Host "Starting servers..." -ForegroundColor Green
Write-Host ""

# Start backend in new window
Write-Host "  Backend: http://localhost:8000" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath'; Write-Host 'BILI Backend Server' -ForegroundColor Green; Write-Host 'URL: http://localhost:8000' -ForegroundColor Cyan; Write-Host 'API Docs: http://localhost:8000/api/docs' -ForegroundColor Cyan; Write-Host ''; python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

# Wait for backend to start
Start-Sleep -Seconds 5

# Start frontend in new window
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$scriptPath\frontend'; Write-Host 'BILI Frontend Server' -ForegroundColor Green; Write-Host 'URL: http://localhost:3000' -ForegroundColor Cyan; Write-Host ''; npm start"

# Wait for servers to initialize
Write-Host ""
Write-Host "Waiting for servers to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 20

# Open browser
Write-Host ""
Write-Host "Opening application..." -ForegroundColor Green
Start-Process "http://localhost:3000"
Start-Sleep -Seconds 2
Start-Process "http://localhost:8000/api/docs"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ✓ Servers Started!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit this window..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
