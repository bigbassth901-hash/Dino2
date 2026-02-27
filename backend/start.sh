#!/bin/bash

echo "Starting Film Asset Management Backend..."

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Creating necessary directories..."
mkdir -p uploads
mkdir -p keyframes
mkdir -p training_data
mkdir -p chroma_db

echo "Starting FastAPI server..."
python main.py
