#!/bin/bash

echo "=================================="
echo "  ALMS - Advanced Library System"
echo "=================================="
echo ""

# Step 1: Check Python
echo "[1/4] Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "ERROR: Python is not installed. Please install Python 3.8+ first."
    exit 1
fi
echo "  Found: $($PYTHON --version)"

# Step 2: Install dependencies
echo ""
echo "[2/4] Installing dependencies..."
$PYTHON -m pip install -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies."
    exit 1
fi
echo "  Dependencies installed."

# Step 3: Seed database
echo ""
echo "[3/4] Setting up database..."
if [ ! -f "instance/lms.db" ]; then
    $PYTHON seed.py
    echo "  Database created with sample data."
else
    echo "  Database already exists. Skipping seed."
    echo "  (Delete instance/lms.db and re-run to reset)"
fi

# Step 4: Start server
echo ""
echo "[4/4] Starting server..."
echo ""
echo "=================================="
echo "  App running at: http://localhost:5001"
echo ""
echo "  Admin:   admin@lms.com / admin123"
echo "  Student: student1@lms.com / student123"
echo ""
echo "  Press Ctrl+C to stop"
echo "=================================="
echo ""
$PYTHON app.py
