#!/bin/bash

# Dr. Annops Dental Clinic - Setup Script for macOS/Linux

echo ""
echo "========================================"
echo "Dr. Annops Dental Clinic Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

echo "[1/5] Creating virtual environment..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment"
    exit 1
fi

echo "[2/5] Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate virtual environment"
    exit 1
fi

echo "[3/5] Installing dependencies..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo "[4/5] Running database migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
    echo "Error: Database migration failed"
    exit 1
fi

echo "[5/5] Creating superuser (admin account)..."
python manage.py createsuperuser

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "To start the development server, run:"
echo "source venv/bin/activate"
echo "python manage.py runserver"
echo ""
echo "Then visit: http://localhost:8000"
echo "Admin panel: http://localhost:8000/admin/"
echo ""
