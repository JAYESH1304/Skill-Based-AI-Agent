@echo off
echo Starting Skill-Based Agent System...
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if dependencies are installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Check if .env exists
if not exist ".env" (
    echo Warning: .env file not found!
    echo Please copy .env.example to .env and configure your Azure OpenAI credentials.
    echo.
    pause
    exit /b 1
)

REM Run the Streamlit app
echo Launching Streamlit application...
echo.
streamlit run ui/streamlit_app.py

pause