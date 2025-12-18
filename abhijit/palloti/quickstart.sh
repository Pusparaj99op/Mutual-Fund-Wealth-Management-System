#!/bin/bash
# Quick start script for Federal Wealth Management System (Mac/Linux)

echo "╔════════════════════════════════════════════════════════╗"
echo "║  Federal Wealth Management System - Quick Start        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9+"
    exit 1
fi

python_version=$(python3 -V 2>&1 | awk '{print $2}')
echo "✓ Python $python_version found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate
echo "✓ Virtual environment created and activated"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"
echo ""

# Initialize system
echo "🚀 Initializing system (this may take 2-5 minutes)..."
python main.py --full

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║  Setup Complete!                                       ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "📌 Next Steps:"
echo "   1. Backend is running on http://localhost:8000"
echo "   2. Start dashboard in new terminal:"
echo "      source venv/bin/activate"
echo "      streamlit run app/dashboard.py"
echo "   3. Open http://localhost:8501 in your browser"
echo ""
echo "📖 API Documentation: http://localhost:8000/docs"
echo ""
