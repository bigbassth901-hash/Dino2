#!/bin/bash

echo "=========================================="
echo "Film Asset Management Backend"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment"
        exit 1
    fi
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Checking pip..."
pip install --upgrade pip > /dev/null 2>&1

echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
fi

echo ""
echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p keyframes
mkdir -p training_data
mkdir -p chroma_db

echo ""
echo "Running tests..."
python3 test_api.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Warning: Some tests failed, but starting server anyway..."
fi

echo ""
echo "=========================================="
echo "Starting FastAPI server on port 8000..."
echo "=========================================="
echo ""

python3 main.py
