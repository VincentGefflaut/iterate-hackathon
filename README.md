# Product Alerts System

An integrated system for monitoring product-related news alerts and visualizing them through a modern React frontend.

## Architecture

The system consists of three main components:

1. **Backend Pipeline** (`run_product_alerts_mvp.py`) - Fetches news, detects product-related events, and generates alerts
2. **API Server** (`api_server.py`) - Flask REST API that serves alerts to the frontend
3. **React Frontend** (`frontend/`) - Modern web interface for viewing and managing alerts

## Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
# Start both API server and frontend
./start_servers.sh
```

This will:
- Create a Python virtual environment if needed
- Install Python dependencies
- Start the Flask API server on port 5000
- Install frontend dependencies
- Start the React dev server on port 5173

### Option 2: Manual Setup

#### 1. Set Up Python Backend

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
# API Keys
NEWS_API_KEY=your_newsapi_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

#### 3. Run the Alert Generation Pipeline

```bash
# Generate alerts for today with default settings
python run_product_alerts_mvp.py

# Custom options
python run_product_alerts_mvp.py --top-n 10 --max-articles 20 --severity medium

# Demo mode (uses sample data)
python run_product_alerts_mvp.py --demo
```

This creates a JSON file at `data/alerts/product_alerts_YYYY-MM-DD.json`

#### 4. Start the API Server

```bash
# Start on default port 5000
python api_server.py

# Custom port
python api_server.py --port 8000

# Debug mode
python api_server.py --debug
```

#### 5. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Create .env file from example
cp .env.example .env

# Update .env with your Supabase credentials
# VITE_SUPABASE_URL=your_supabase_url
# VITE_SUPABASE_ANON_KEY=your_supabase_key
# VITE_API_URL=http://localhost:5000

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

The Flask API server provides the following endpoints:

### Health Check
```
GET /api/health
```
Returns server status and configuration.

### Get Latest Alerts
```
GET /api/alerts/latest
```
Returns the most recently generated alerts.

### Get Alerts by Date
```
GET /api/alerts/<date>
```
Returns alerts for a specific date (format: YYYY-MM-DD).

Example: `GET /api/alerts/2025-11-15`

### List Available Dates
```
GET /api/alerts/list
```
Returns all dates for which alerts are available.

### Get Summary
```
GET /api/alerts/summary
```
Returns a summary of all alerts including severity breakdown.

## How It Works

### 1. Alert Generation Pipeline

The `run_product_alerts_mvp.py` script:

1. Loads top products from `top.csv`
2. Fetches relevant news articles (via NewsAPI or RSS feeds)
3. Uses Claude AI to detect product-related events
4. Generates alerts with severity levels and recommended actions
5. Saves results to `data/alerts/product_alerts_{date}.json`

### 2. API Layer

The Flask API server:

1. Monitors the `data/alerts/` directory
2. Serves alerts via REST endpoints
3. Enables CORS for frontend access
4. Provides metadata and summaries

### 3. Frontend

The React frontend:

1. Automatically fetches latest alerts on load
2. Stores alerts in Supabase for persistence
3. Displays alerts with filtering and sorting
4. Allows manual JSON import as fallback

## Data Flow

```
run_product_alerts_mvp.py
    ↓
data/alerts/product_alerts_YYYY-MM-DD.json
    ↓
api_server.py (Flask)
    ↓
React Frontend → Supabase
```

## Alert JSON Structure

```json
{
  "date": "2025-11-15",
  "generated_at": "2025-11-15T10:30:00",
  "total_alerts": 5,
  "severity_threshold": "medium",
  "tracked_locations": ["Dublin", "Cork", "Galway"],
  "tracked_products": ["Vitamin D", "Serum", "Cleanser"],
  "alerts": [
    {
      "alert_id": "evt_abc123",
      "event_type": "shortage",
      "title": "Vitamin D Shortage in Dublin",
      "severity": "high",
      "urgency": "immediate",
      "affected_products": ["Vitamin D"],
      "affected_areas": ["Dublin", "Cork"],
      "location": "Ireland",
      "event_date": "2025-11-15",
      "description": "...",
      "key_facts": ["..."],
      "potential_relevance": "...",
      "recommended_action": "...",
      "source_url": "https://..."
    }
  ]
}
```

## Configuration

### Backend Configuration

Environment variables (`.env`):
- `NEWS_API_KEY` - NewsAPI key for fetching articles
- `ANTHROPIC_API_KEY` - Anthropic API key for Claude AI

Command-line options for `run_product_alerts_mvp.py`:
- `--top-n N` - Monitor top N locations (default: 5)
- `--max-articles N` - Process up to N articles (default: 10)
- `--severity LEVEL` - Minimum severity level (low/medium/high/critical)
- `--demo` - Run in demo mode with sample data

### API Server Configuration

Command-line options for `api_server.py`:
- `--port PORT` - Port to run on (default: 5000)
- `--host HOST` - Host to bind to (default: 0.0.0.0)
- `--debug` - Enable debug mode

### Frontend Configuration

Environment variables (`frontend/.env`):
- `VITE_API_URL` - API server URL (default: http://localhost:5000)
- `VITE_SUPABASE_URL` - Supabase project URL
- `VITE_SUPABASE_ANON_KEY` - Supabase anonymous key

## Troubleshooting

### No alerts appear in frontend

1. Check if API server is running: `curl http://localhost:5000/api/health`
2. Verify alerts exist: `ls -la data/alerts/`
3. Generate alerts: `python run_product_alerts_mvp.py --demo`
4. Click "Actualiser" button in frontend

### API connection failed

1. Verify API server is running on correct port
2. Check `VITE_API_URL` in `frontend/.env`
3. Check browser console for CORS errors
4. Ensure Flask and flask-cors are installed

### No news articles fetched

1. Set `NEWS_API_KEY` in `.env`
2. Check internet connection
3. Try `--demo` mode to test with sample data

### Claude AI errors

1. Verify `ANTHROPIC_API_KEY` is set correctly
2. Check API quota/credits
3. Review error messages in console output

## Development

### Running Tests

```bash
# Backend tests
python test_mvp_components.py
python test_data_integration.py

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Frontend production build
cd frontend
npm run build

# Output in frontend/dist/
```

## Project Structure

```
iterate-hackathon/
├── run_product_alerts_mvp.py    # Main alert generation pipeline
├── api_server.py                 # Flask API server
├── start_servers.sh              # Startup script
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (not in git)
├── data/
│   ├── alerts/                   # Generated alert JSON files
│   └── top.csv                   # Top products data
├── news_alerts/                  # Alert generation modules
│   ├── product_news_fetcher.py
│   ├── product_event_detector.py
│   └── ...
└── frontend/                     # React application
    ├── src/
    │   ├── pages/
    │   │   └── Alerts.tsx        # Main alerts page
    │   └── ...
    ├── .env                      # Frontend environment variables
    └── package.json
```

## Contributing

When making changes:

1. Update relevant documentation
2. Test both API and frontend
3. Ensure backward compatibility
4. Update version numbers

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
