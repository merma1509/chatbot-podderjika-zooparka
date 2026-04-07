# Task 4: Windows PowerShell Setup Script
Write-Host "=== Task 4: Windows Setup Script ===" -ForegroundColor Green
Write-Host "Setting up virtual environment and dependencies..." -ForegroundColor Yellow

# Check if venvs exists
if (-not (Test-Path "venvs")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    py -m venv venvs
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venvs\Scripts\Activate.ps1"

# Check Python version
Write-Host "Python version:" -ForegroundColor Cyan
python --version

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
py -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host ""
Write-Host "=== Setup Complete ===" -ForegroundColor Green
Write-Host "Virtual environment is activated." -ForegroundColor Green
Write-Host "You can now run the deployment scripts." -ForegroundColor Green
Write-Host ""
Write-Host "To run Task 4:" -ForegroundColor Cyan
Write-Host "  cd zadanie4"
Write-Host "  python local_llm_server.py --model-type lm_studio"
Write-Host ""
Write-Host "Or use the deployment script:" -ForegroundColor Cyan
Write-Host "  bash working_deploy.sh"
Write-Host ""

Write-Host "Press any key to continue..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
