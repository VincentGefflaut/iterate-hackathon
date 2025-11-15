#!/bin/bash
# Launch Interactive Demo Dashboard
#
# This script starts the interactive web demo where you can:
# - Select any date from your data
# - Run the alert pipeline on demand
# - View results in real-time
#
# Perfect for demos and presentations!

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        Interactive Alerts Demo Dashboard                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo

# Check if Python is available
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.7+"
    exit 1
fi

# Check and install dependencies
echo "📦 Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "Installing Flask..."
    pip install flask flask-cors -q
fi

if ! python -c "import pandas" 2>/dev/null; then
    echo "Installing pandas..."
    pip install pandas -q
fi

echo "✅ Dependencies ready"
echo

# Generate some demo alerts if none exist
if [ ! -d "data/alerts" ] || [ -z "$(ls -A data/alerts/*.json 2>/dev/null)" ]; then
    echo "📊 Generating demo alerts..."
    python run_full_pipeline.py --demo 2>/dev/null || true
    echo
fi

# Start the server
echo "🚀 Starting demo server..."
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  🌐 Open your browser to:"
echo
echo "      http://localhost:5000"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  💡 Usage:"
echo "     1. Select a date from the dropdown"
echo "     2. Click 'Run Pipeline' button"
echo "     3. Watch the progress bar"
echo "     4. View generated alerts below"
echo
echo "  🎯 Demo Mode: Fast, no API keys needed"
echo "  📊 Real Data: Uses actual sales/inventory (if available)"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo
echo "  Press Ctrl+C to stop the server"
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo

# Launch server
python demo_server.py
