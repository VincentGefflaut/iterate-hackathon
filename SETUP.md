# Setup Guide - News Alerts System

Complete setup instructions for the News Alerts event detection system.

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/VincentGefflaut/iterate-hackathon.git
cd iterate-hackathon
```

### 2. Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `anthropic` - Claude AI API client
- `requests` - HTTP library for news fetching
- `pydantic` - Data validation and modeling
- `python-dotenv` - Environment variable management
- `pandas`, `numpy`, `scipy` - Data processing (for alert_features)

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual API keys
nano .env  # or use your preferred editor
```

**Required:**
```bash
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

**Optional:**
```bash
NEWS_API_KEY=your-newsapi-key-here
```

### 5. Get API Keys

#### Anthropic API Key (Required)

1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to "API Keys"
4. Create a new API key
5. Copy the key to your `.env` file

**Pricing:**
- Pay as you go
- Claude 3.5 Sonnet: ~$0.003 per article
- Estimated cost: $9-45/month depending on usage

#### NewsAPI Key (Optional)

1. Go to https://newsapi.org/register
2. Sign up for a free account
3. Copy your API key to your `.env` file

**Free Tier:**
- 100 requests/day
- Good for testing and light production use

**Note:** If you don't have a NewsAPI key, the system will still work with:
- Google News RSS (may be blocked by some networks)
- Met Éireann weather alerts
- Demo mode with sample articles

### 6. Verify Installation

Test that everything is working:

```bash
# Check if packages are installed
python -c "import anthropic, requests, pydantic, dotenv; print('✓ All packages installed')"

# Check if environment variables are loaded
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('✓ API key loaded' if os.getenv('ANTHROPIC_API_KEY') else '✗ API key not found')"
```

### 7. Run Demo Mode

Test the system with sample articles:

```bash
python run_news_alerts.py --demo
```

**Expected output:**
```
================================================================================
DEMO MODE - Testing Event Detection
================================================================================

Testing with 3 sample articles:

1. Testing: Norovirus Outbreak Spreads Across Dublin Hospitals
   Source: Irish Times
   ✓ DETECTED: health_emergency
     Severity: high
     Confidence: high
     Urgency: immediate
     ...

Demo complete. Detected 2 events.
================================================================================
```

## Directory Structure

After setup, your project should look like this:

```
iterate-hackathon/
├── .env                           # Your API keys (not in git)
├── .env.example                   # Example env file (template)
├── requirements.txt               # Python dependencies
├── run_news_alerts.py            # Main CLI script
│
├── news_alerts/                   # Event detection package
│   ├── __init__.py
│   ├── models.py
│   ├── news_fetcher.py
│   ├── event_detector.py
│   ├── event_storage.py
│   └── README.md
│
├── alert_features/                # Feature engineering package
│   ├── __init__.py
│   ├── daily_aggregator.py
│   ├── alert_features.py
│   ├── anomaly_detector.py
│   └── ...
│
├── data/
│   ├── events/                    # Detected events storage
│   │   ├── events_YYYY-MM-DD.json
│   │   └── report_YYYY-MM-DD.json
│   ├── cache/                     # Feature cache
│   └── input/                     # Input data files
│
└── docs/                          # Documentation
    ├── NEWS_ALERTS_QUICKSTART.md
    ├── SETUP.md                   # This file
    └── ...
```

## Usage

### Demo Mode (Testing)

```bash
python run_news_alerts.py --demo
```

### Production Modes

```bash
# Detect all event types (health + major events)
python run_news_alerts.py

# Only health emergencies
python run_news_alerts.py --health-only

# Only major events (concerts, festivals, etc.)
python run_news_alerts.py --events-only

# View statistics
python run_news_alerts.py --stats
```

### Output Location

Detected events are stored in `data/events/`:
- `events_YYYY-MM-DD.json` - Individual events for the day
- `report_YYYY-MM-DD.json` - Daily summary report

## Troubleshooting

### "ModuleNotFoundError: No module named 'anthropic'"

**Solution:**
```bash
pip install -r requirements.txt
```

### "ANTHROPIC_API_KEY must be provided"

**Solution:**
1. Make sure `.env` file exists in project root
2. Check that `ANTHROPIC_API_KEY=your-key` is set in `.env`
3. Verify the key is valid (no extra spaces or quotes)

**Test:**
```bash
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('ANTHROPIC_API_KEY'))"
```

### "403 Forbidden" errors from Google News

**Expected behavior.** Google News blocks automated RSS access.

**Solutions:**
- Use NewsAPI with a valid API key
- Use demo mode for testing
- Run in production with NewsAPI integration

### "No articles found"

**Possible causes:**
1. Google News RSS is blocked (expected)
2. NewsAPI key not set or invalid
3. Network/firewall blocking requests

**Solutions:**
- Set NEWS_API_KEY in `.env`
- Use demo mode
- Check network connectivity

### Virtual environment not activating

**On Linux/Mac:**
```bash
source venv/bin/activate
```

**On Windows:**
```bash
venv\Scripts\activate
```

**On Windows (PowerShell):**
```bash
venv\Scripts\Activate.ps1
```

### Permission denied when creating directories

**Solution:**
```bash
# Make sure you have write permissions
chmod -R u+w data/

# Or run with appropriate permissions
sudo python run_news_alerts.py  # Not recommended, use virtual env instead
```

## Next Steps

### 1. Test with Real News

Once API keys are configured:

```bash
# Run health emergency detection
python run_news_alerts.py --health-only

# Check results
ls -la data/events/
```

### 2. Setup Daily Automation

Create a cron job to run daily:

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 6:00 AM)
0 6 * * * cd /path/to/iterate-hackathon && /path/to/venv/bin/python run_news_alerts.py >> /path/to/logs/news_alerts.log 2>&1
```

### 3. Integrate with Alert Features

Build the Context Matcher to connect detected events with business features:

```python
from news_alerts import EventStorage
from alert_features import AlertFeatureCalculator

# Load detected events
storage = EventStorage()
events = storage.get_recent_events(days=1)

# Match against business data
calculator = AlertFeatureCalculator(sales_df, inventory_df)
for event in events:
    if event.event_type == "health_emergency":
        features = calculator.get_health_emergency_features(...)
        # Decision logic...
```

### 4. Build Dashboard

Create a Streamlit dashboard for visualization:

```bash
pip install streamlit
streamlit run dashboard.py
```

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ANTHROPIC_API_KEY` | Yes | None | Claude AI API key for event detection |
| `NEWS_API_KEY` | No | None | NewsAPI.org key for news fetching (100 free/day) |

## Development Setup

For development work:

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black ruff

# Run tests (when available)
pytest tests/

# Format code
black news_alerts/
ruff check news_alerts/
```

## Production Deployment

### Option 1: Cron Job (Simple)

```bash
# Create log directory
mkdir -p logs

# Add to crontab
0 6 * * * cd /path/to/project && ./venv/bin/python run_news_alerts.py >> logs/news_alerts.log 2>&1
```

### Option 2: Systemd Service (Linux)

Create `/etc/systemd/system/news-alerts.service`:

```ini
[Unit]
Description=News Alerts Event Detection
After=network.target

[Service]
Type=oneshot
User=youruser
WorkingDirectory=/path/to/iterate-hackathon
Environment="PATH=/path/to/iterate-hackathon/venv/bin"
ExecStart=/path/to/iterate-hackathon/venv/bin/python run_news_alerts.py

[Install]
WantedBy=multi-user.target
```

Create timer `/etc/systemd/system/news-alerts.timer`:

```ini
[Unit]
Description=Run News Alerts Daily

[Timer]
OnCalendar=daily
OnCalendar=06:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:
```bash
sudo systemctl enable news-alerts.timer
sudo systemctl start news-alerts.timer
```

### Option 3: Docker (Portable)

```bash
# Build image
docker build -t news-alerts .

# Run
docker run -v $(pwd)/data:/app/data --env-file .env news-alerts
```

## Security Best Practices

1. **Never commit .env file** - Already in .gitignore
2. **Use strong API keys** - Rotate regularly
3. **Limit API key permissions** - Use read-only keys where possible
4. **Monitor usage** - Track API costs and rate limits
5. **Secure storage directory** - Restrict permissions on `data/events/`

```bash
# Restrict access to .env
chmod 600 .env

# Restrict access to events directory
chmod 700 data/events/
```

## Cost Monitoring

### Anthropic API Usage

Check your usage at: https://console.anthropic.com/settings/billing

**Estimated costs:**
- 100 articles/day: ~$9/month
- 500 articles/day: ~$45/month
- 1000 articles/day: ~$90/month

### NewsAPI Usage

Check your usage at: https://newsapi.org/account

**Free tier limit:** 100 requests/day

## Support

If you encounter issues:

1. Check this SETUP.md guide
2. Review NEWS_ALERTS_QUICKSTART.md for usage examples
3. Check the troubleshooting section above
4. Verify API keys are correct and valid
5. Test with demo mode first

## Quick Reference

```bash
# Installation
pip install -r requirements.txt

# Setup .env
cp .env.example .env
# Edit .env with your API keys

# Test installation
python run_news_alerts.py --demo

# Run detection
python run_news_alerts.py --health-only

# View results
ls data/events/
cat data/events/report_$(date +%Y-%m-%d).json
```

## Success Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file created with ANTHROPIC_API_KEY
- [ ] Demo mode runs successfully
- [ ] Events stored in data/events/
- [ ] Production mode tested (optional)
- [ ] Cron job or automation configured (optional)

**You're ready to detect black swan events! 🦢**
