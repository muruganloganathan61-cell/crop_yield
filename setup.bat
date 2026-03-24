@echo off
REM Setup script for Windows

echo.
echo ========================================
echo Crop Yield Prediction System - Setup
echo ========================================
echo.

REM Check Python installation
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Python not found!
    echo Please install Python 3.8+ from https://www.python.org/
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found: %PYTHON_VERSION%
echo.

REM Create virtual environment (optional)
echo Setting up Python environment...
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
) else (
    echo Virtual environment already exists
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Train ML Models
echo.
echo Training ML models...
echo.
cd ml_models
pip install -q -r requirements.txt
echo Running train_models.py...
python train_models.py
if errorlevel 1 (
    echo.
    echo ERROR: Model training failed!
    pause
    exit /b 1
)
echo.

REM Setup Backend
echo Setting up Backend...
cd ..\backend
pip install -q -r requirements.txt
echo Backend dependencies installed

REM Summary
echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Open two new PowerShell/Command Prompt windows
echo.
echo 2. In Window 1 (Backend):
echo    cd backend
echo    python app.py
echo.
echo 3. In Window 2 (Frontend):
echo    cd frontend
echo    python -m http.server 8000
echo.
echo 4. Open browser:
echo    http://localhost:8000
echo.
echo For more information, see README.md
echo.
pause
