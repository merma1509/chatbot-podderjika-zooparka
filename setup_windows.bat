@echo off
echo === Task 4: Windows Setup Script ===
echo Setting up virtual environment and dependencies...

REM Check if venvs exists
if not exist "venvs" (
    echo Creating virtual environment...
    py -m venv venvs
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venvs\Scripts\activate.bat

REM Check Python version
echo Python version:
python --version

REM Install dependencies
echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo === Setup Complete ===
echo Virtual environment is activated.
echo You can now run the deployment scripts.
echo.
echo To run Task 4:
echo   cd zadanie4
echo   python local_llm_server.py --model-type lm_studio
echo.
echo Or use the deployment script:
echo   bash working_deploy.sh
echo.

pause
