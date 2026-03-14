@echo off
echo ========================================
echo Skill-Based Agent System - Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo Step 1: Creating virtual environment...
python -m venv venv
echo Virtual environment created successfully!
echo.

echo Step 2: Activating virtual environment...
call venv\Scripts\activate.bat
echo.

echo Step 3: Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt
echo Dependencies installed successfully!
echo.

echo Step 4: Setting up configuration...
if not exist ".env" (
    copy .env.example .env
    echo .env file created from template
    echo.
    echo IMPORTANT: Please edit .env file and add your Azure OpenAI credentials
    echo You can edit it in VS Code or any text editor
) else (
    echo .env file already exists
)
echo.

echo Step 5: Creating skills directory...
if not exist "skills\" (
    mkdir skills
    echo Skills directory created
)
echo.

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Edit .env file with your Azure OpenAI credentials
echo 2. Run: run.bat (or 'streamlit run ui/streamlit_app.py')
echo.
echo To activate the virtual environment manually:
echo   venv\Scripts\activate.bat
echo.
pause