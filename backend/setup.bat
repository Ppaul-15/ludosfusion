@echo off
REM Setup script for Color Educational Platform Backend (Windows)

echo.
echo 🚀 Color Educational Platform - Backend Setup
echo ==============================================
echo.

REM Check Python version
echo ✅ Checking Python installation...
python --version
if errorlevel 1 (
    echo ❌ Python not found. Please install Python from python.org
    exit /b 1
)

REM Create virtual environment
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    exit /b 1
)

REM Create .env if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Update .env with your database credentials
) else (
    echo ✅ .env file already exists
)

echo.
echo ✅ Setup complete!
echo.
echo 📝 Next steps:
echo 1. Update .env with your PostgreSQL credentials
echo 2. Make sure PostgreSQL is running
echo 3. Run: python -m uvicorn app:app --reload
echo.
echo 🌐 Backend will be available at: http://localhost:8000
echo.
pause
