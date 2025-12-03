@echo off
echo 🚀 Starting Automated Insight Engine...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Check for API key
if "%OPENAI_API_KEY%"=="" (
    echo.
    echo ⚠️  WARNING: OPENAI_API_KEY not set!
    echo Please set your API key:
    echo set OPENAI_API_KEY=sk-your-key-here
    echo.
    pause
)

REM Start the application
echo.
echo 🌐 Starting web interface...
echo Open your browser to: http://localhost:8501
echo.
streamlit run app.py

pause