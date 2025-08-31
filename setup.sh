#!/bin/bash

# Setup script for Table & Image Search API

echo "🛠️  Setting up Table & Image Search API"
echo "======================================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or later"
    exit 1
fi

# Virtual environment directory
VENV_DIR="venv"

# Create virtual environment
if [ -d "$VENV_DIR" ]; then
    echo "⚠️  Virtual environment already exists. Removing old one..."
    rm -rf "$VENV_DIR"
fi

echo "📦 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "❌ Error: requirements.txt not found"
    exit 1
fi

echo "✅ Setup completed successfully!"
echo ""
echo "To activate the virtual environment manually:"
echo "  source venv/bin/activate"
echo ""
echo "To start the server:"
echo "  ./start_server.sh"
echo ""
echo "To run sample queries:"
echo "  source venv/bin/activate"
echo "  export OPENAI_API_KEY='your-api-key-here'"
echo "  python run_samples.py"
