@echo off
REM Dr. Annops Dental Clinic - Setup Script for Windows

echo.
echo ========================================
echo Dr. Annops Dental Clinic Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if %errorlevel% neq 0 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error: Database migration failed
    pause
    exit /b 1
)

echo [5/5] Creating superuser (admin account)...
python manage.py createsuperuser

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To start the development server, run:
echo python manage.py runserver
echo.
echo Then visit: http://localhost:8000
echo Admin panel: http://localhost:8000/admin/
echo.
pause
