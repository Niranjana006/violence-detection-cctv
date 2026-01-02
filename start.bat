@echo off
echo ===================================================
echo     🛡️ Violence Detection System - Starting...
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo ✅ Python found
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Failed to create virtual environment
        pause
        exit /b 1
    )
    echo ✅ Virtual environment created
)

echo 🔄 Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\streamlit" (
    echo 📦 Installing dependencies (this may take a few minutes)...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ Failed to install dependencies
        pause
        exit /b 1
    )
    echo ✅ Dependencies installed successfully
)

REM Create necessary directories
if not exist "models" mkdir models
if not exist "uploads" mkdir uploads
if not exist "screenshots" mkdir screenshots

REM Check if model file exists
if not exist "models\best_mobilenet_bilstm.h5" (
    echo.
    echo ⚠️  WARNING: Model file not found!
    echo Please copy your trained model file to:
    echo    models\best_mobilenet_bilstm.h5
    echo.
    echo The system will still start, but video analysis won't work
    echo until you add the model file.
    echo.
    timeout /t 5 /nobreak
)

REM Check if config file exists
if not exist ".env" (
    echo 📝 Creating configuration file...
    copy config_template.env .env
    echo ✅ Configuration file created
    echo.
    echo ⚠️  Please edit .env file to configure email settings
    echo.
)

echo 🚀 Starting Violence Detection System...
echo.
echo 📱 Your application will open in your default browser
echo 🌐 URL: http://localhost:8501
echo.
echo ⚠️  Do NOT close this window while using the application
echo 🛑 Press Ctrl+C to stop the application
echo.

REM Start the Streamlit application
streamlit run app.py --server.port 8501 --server.address localhost

echo.
echo 👋 Violence Detection System stopped
pause