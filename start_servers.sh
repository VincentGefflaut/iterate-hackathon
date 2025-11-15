#!/bin/bash
# Start both the Flask API server and the React frontend

echo "================================================"
echo "  Starting Product Alerts Application"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}No virtual environment found. Creating one...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${GREEN}Activating virtual environment...${NC}"
source venv/bin/activate

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt

# Start Flask API server in background
echo -e "${GREEN}Starting Flask API server on port 5000...${NC}"
python api_server.py --port 5000 &
API_PID=$!
echo "API server PID: $API_PID"

# Wait a moment for API to start
sleep 2

# Start frontend development server
echo ""
echo -e "${GREEN}Starting React frontend...${NC}"
cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}Please update .env with your Supabase credentials${NC}"
fi

# Start frontend
npm run dev &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

echo ""
echo "================================================"
echo -e "${GREEN}  Servers started successfully!${NC}"
echo "================================================"
echo ""
echo "  API Server:      http://localhost:5000"
echo "  Frontend:        http://localhost:5173"
echo ""
echo "  Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on Ctrl+C
trap cleanup INT TERM

# Wait for both processes
wait
