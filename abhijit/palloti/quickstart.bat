@echo off
REM Quick start script for Federal Wealth Management System (Windows)

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Federal Wealth Management System - Quick Start        ║
echo ╚════════════════════════════════════════════════════════╝
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.9+
    pause
    exit /b 1
)

echo ✓ Python found
echo.

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat
echo ✓ Virtual environment created and activated
echo.

REM Install dependencies
echo 📚 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt
echo ✓ Dependencies installed
echo.

REM Initialize system
echo 🚀 Initializing system (this may take 2-5 minutes)...
python main.py --full

echo.
echo ╔════════════════════════════════════════════════════════╗
echo ║  Setup Complete!                                       ║
echo ╚════════════════════════════════════════════════════════╝
echo.
echo 📌 Next Steps:
echo    1. Backend is running on http://localhost:8000
echo    2. Start dashboard in new terminal:
echo       venv\Scripts\activate.bat
echo       streamlit run app/dashboard.py
echo    3. Open http://localhost:8501 in your browser
echo.
echo 📖 API Documentation: http://localhost:8000/docs
echo.
pause
