# BMAD Dash - Start Dashboard Server (PowerShell)
# Right-click and select "Run with PowerShell" to start

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BMAD Dash - Starting Dashboard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Kill any existing Flask servers on port 5000
Write-Host "Checking for existing server..." -ForegroundColor Yellow
$connections = Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue
if ($connections) {
    foreach ($conn in $connections) {
        Write-Host "Stopping existing server (PID: $($conn.OwningProcess))" -ForegroundColor Yellow
        Stop-Process -Id $conn.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "Starting Flask backend server..." -ForegroundColor Green
Write-Host ""

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Start the Flask server in a new window
Start-Process -FilePath "python" -ArgumentList "-m","backend.app" -WorkingDirectory $scriptDir -WindowStyle Normal

# Wait for server to start
Write-Host "Waiting for server to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Open browser
Write-Host "Opening dashboard in browser..." -ForegroundColor Green
Start-Process "http://localhost:5000"

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Dashboard should now be open!" -ForegroundColor Green
Write-Host "Keep the Python window running." -ForegroundColor Yellow
Write-Host "Close it to stop the server." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to close this window..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
