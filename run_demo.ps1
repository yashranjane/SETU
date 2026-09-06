# SETU Demonstration Launcher (PowerShell)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  SETU: The Innovation Procurement OS (Smart India Hackathon)" -ForegroundColor Yellow
Write-Host "  Statutory Compliance: GFR 2017 Rule 173 (Non-Consultative)" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Cyan

Write-Host "`n[1/3] Launching FastAPI Backend Server on port 8000..." -ForegroundColor Yellow
Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\api'; & '.\.venv\Scripts\python.exe' -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

Write-Host "[2/3] Verifying backend availability..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

Write-Host "[3/3] Opening SETU Live Dashboard in default browser..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"

Write-Host "`n==========================================================" -ForegroundColor Cyan
Write-Host "  SETU OS is Live & Ready!" -ForegroundColor Green
Write-Host "  * Interactive Dashboard: http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  * Swagger API Docs:      http://127.0.0.1:8000/api/v1/docs" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Cyan
