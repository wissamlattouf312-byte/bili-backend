# Wait for servers to be ready and open Chrome
Write-Host "Waiting for servers to be fully ready..." -ForegroundColor Yellow
Write-Host "Monitoring backend (8000) and frontend (3000)..." -ForegroundColor Cyan

$maxAttempts = 90
$attempt = 0
$backendReady = $false
$frontendReady = $false

while ($attempt -lt $maxAttempts -and (-not $backendReady -or -not $frontendReady)) {
    $attempt++
    Start-Sleep -Seconds 2
    
    # Check backend
    if (-not $backendReady) {
        $backend = Test-NetConnection -ComputerName localhost -Port 8000 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($backend) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    $backendReady = $true
                    Write-Host "Backend (8000): READY ✓" -ForegroundColor Green
                }
            } catch {}
        }
    }
    
    # Check frontend
    if (-not $frontendReady) {
        $frontend = Test-NetConnection -ComputerName localhost -Port 3000 -InformationLevel Quiet -WarningAction SilentlyContinue
        if ($frontend) {
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -UseBasicParsing -ErrorAction Stop
                if ($response.StatusCode -eq 200 -and $response.Content -match "BILI|React") {
                    $frontendReady = $true
                    Write-Host "Frontend (3000): READY ✓ (Compiled successfully)" -ForegroundColor Green
                }
            } catch {}
        }
    }
    
    # Progress update every 10 seconds
    if ($attempt % 5 -eq 0) {
        Write-Host "Checking... Backend: $(if($backendReady){'READY'}else{'WAITING'}), Frontend: $(if($frontendReady){'READY'}else{'WAITING'})" -ForegroundColor Yellow
    }
}

Write-Host ""
if ($backendReady -and $frontendReady) {
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Both servers are READY!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Start-Sleep -Seconds 2
    Start-Process chrome.exe -ArgumentList "http://localhost:3000"
    Write-Host "Chrome opened/refreshed to http://localhost:3000" -ForegroundColor Green
    Write-Host ""
    Write-Host "✓ Claim button '20 حبة' should be visible" -ForegroundColor Cyan
    Write-Host "✓ Guest mode is active by default" -ForegroundColor Cyan
} else {
    Write-Host "Servers may still be starting. Opening Chrome..." -ForegroundColor Yellow
    Start-Process chrome.exe -ArgumentList "http://localhost:3000"
}
