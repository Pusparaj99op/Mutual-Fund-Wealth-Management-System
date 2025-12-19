#!/bin/bash

# FIMFP - Federal Indian Mutual Fund Portal
# Startup Script

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                                                               ║"
echo "║   🇮🇳 FIMFP - Federal Indian Mutual Fund Portal 🇮🇳           ║"
echo "║   भारतीय संघीय म्यूचुअल फंड पोर्टल                            ║"
echo "║                                                               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    echo "Please install Python 3.8 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if required packages are installed
echo ""
echo "🔍 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not found. Installing dependencies..."
    pip install -r requirements.txt
else
    echo "✓ Dependencies already installed"
fi

echo ""
echo "🚀 Starting FIMFP API Server..."
echo ""
echo "📍 Server will be available at: http://localhost:8009"
echo "📍 API Documentation: http://localhost:8009/api/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo ""

# Start the Flask server
cd api
python3 app.py
