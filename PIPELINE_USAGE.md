# News Alerts Pipeline - Complete Usage Guide

## Overview

The News Alerts system is a two-agent pipeline that detects events from news sources and generates actionable business alerts for retail pharmacy operations.

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWS ALERTS PIPELINE                         │
└─────────────────────────────────────────────────────────────────┘

Step 1: Data Engineering (Optional)
├── Build alert features from sales/inventory data
├── Calculate baselines, consumption rates, traffic patterns
└── Cache features for fast retrieval
    ↓
Step 2: News Fetching & Event Detection (Agent 1)
├── Fetch news from multiple sources (NewsAPI, Google News, Met Éireann)
├── Use Claude Sonnet 4.5 to extract structured events
├── Store detected events as JSON
└── Generate daily event report
    ↓
Step 3: Context Matching (Agent 2)
├── Load detected events
├── Match against business context (rules + optional real data)
├── Enhance with LLM explanations (optional)
└── Generate actionable alerts with playbooks
    ↓
Output: Business Alerts + Daily Report
```

## Quick Start

### 1. Full Pipeline (One Command)

Run the entire pipeline for a specific date:

```bash
# Run for today (heuristic mode, no data needed)
python run_full_pipeline.py

# Run for specific date
python run_full_pipeline.py --date 2024-11-15

# Use real business data for better decisions
python run_full_pipeline.py --date 2024-11-15 --use-real-data

# Faster mode (skip LLM enhancements)
python run_full_pipeline.py --date 2024-11-15 --no-llm

# Demo mode (no API calls, uses mock data)
python run_full_pipeline.py --demo
```

### 2. Step-by-Step Execution

Run each step individually for more control:

#### Step 1: Build Alert Features (Optional)

Only needed if using `--use-real-data` mode:

```bash
# Build features for yesterday
python build_alert_features.py

# Build for specific date
python build_alert_features.py --date 2024-11-15

# Build for date range
python build_alert_features.py --start 2024-10-01 --end 2024-10-31

# Show demo of all available features
python build_alert_features.py --demo
```

#### Step 2: News Fetching & Event Detection (Agent 1)

```bash
# Fetch news and detect events (production)
python run_news_alerts.py --max-articles 50

# Demo mode (no API calls)
python run_news_alerts.py --demo

# Focus on specific event types
python run_news_alerts.py --focus health --max-articles 30
```

#### Step 3: Context Matching (Agent 2)

```bash
# Generate alerts from detected events
python run_context_matcher.py --date 2024-11-15

# Use real business data
python run_context_matcher.py --date 2024-11-15 --use-real-data

# Disable LLM enhancements (faster, cheaper)
python run_context_matcher.py --date 2024-11-15 --no-llm

# Show alert statistics
python run_context_matcher.py --stats
```

## Operating Modes

### Heuristic Mode (Default)

**What it does:**
- Keyword matching for event classification
- Severity-based alert thresholds
- Generic playbook actions

**Requirements:**
- ✅ ANTHROPIC_API_KEY (for event detection)
- ❌ No data files needed

**Use when:**
- Getting started
- No historical data available
- Quick testing

**Example:**
```bash
python run_full_pipeline.py --date 2024-11-15
```

---

### Data-Driven Mode (Recommended)

**What it does:**
- Real inventory levels and consumption rates
- Days of supply calculations (outbreak vs normal)
- Traffic pattern analysis
- Specific supplier recommendations

**Requirements:**
- ✅ ANTHROPIC_API_KEY (for event detection)
- ✅ Sales CSV: `data/input/Retail/retail_sales_data_*.csv`
- ✅ Inventory CSV: `data/input/Retail/retail_inventory_snapshot_*.csv`

**Use when:**
- You have historical data
- Need accurate inventory decisions
- Production deployments

**Example:**
```bash
python run_full_pipeline.py --date 2024-11-15 --use-real-data
```

---

### Demo Mode (No API Keys)

**What it does:**
- Uses mock events (no news fetching)
- Shows example pipeline outputs
- Fast execution

**Requirements:**
- ❌ No API keys needed
- ❌ No data files needed

**Use when:**
- Testing the pipeline
- No API access
- Quick demonstrations

**Example:**
```bash
python run_full_pipeline.py --demo
```

## Configuration Options

### LLM Enhancements

Control whether LLM adds rich explanations to alerts:

```bash
# With LLM (default) - Rich insights, ~$0.01/alert
python run_context_matcher.py --date 2024-11-15

# Without LLM - Rules only, $0 cost, faster
python run_context_matcher.py --date 2024-11-15 --no-llm
```

**LLM Enhancement Benefits:**
- ✅ Natural language business impact summary
- ✅ Enhanced action recommendations
- ✅ Risk assessment
- ✅ Manager talking points

**Cost Comparison:**
- Rules only: $0 per alert (instant)
- Rules + LLM: ~$0.01 per alert (1-2 seconds)

### Article Limits

Control how many articles to process:

```bash
# Default: 50 articles
python run_news_alerts.py

# Process more articles (higher cost)
python run_news_alerts.py --max-articles 100

# Quick test with fewer articles
python run_news_alerts.py --max-articles 10
```

**Cost Estimate:**
- ~$0.03 per article for event extraction
- 50 articles ≈ $1.50
- 100 articles ≈ $3.00

## Output Files

### Detected Events

Location: `data/events/`

```bash
# View events for a date
cat data/events/events_2024-11-15.json

# View daily report
cat data/events/report_2024-11-15.json
```

**Structure:**
```json
{
  "event_type": "health_emergency",
  "title": "Norovirus Outbreak in Dublin",
  "severity": "high",
  "urgency": "immediate",
  "location": "Dublin, Ireland",
  "key_facts": [...],
  "potential_relevance": "..."
}
```

### Business Alerts

Location: `data/alerts/`

```bash
# View all alerts for a date
ls data/alerts/alert_2024-11-15_*.json

# View daily report
cat data/alerts/daily_report_2024-11-15.json
```

**Structure:**
```json
{
  "alert_type": "health_emergency",
  "severity": "critical",
  "urgency": "immediate",
  "affected_categories": ["OTC : GIT", "Hand Sanitizer"],
  "affected_locations": ["Baggot St", "Grafton St"],
  "decision": {
    "confidence": 0.95,
    "reasoning": [
      "📊 DATA: Current stock = 1234 units",
      "📊 DATA: Days of supply at outbreak rate = 3.2 days",
      "🚨 CRITICAL: Only 3.2 days of supply!"
    ]
  },
  "immediate_actions": [...],
  "short_term_actions": [...],
  "playbook_name": "Health Emergency - Critical Response"
}
```

### Alert Features (Optional)

Location: `data/cache/daily_features/`

```bash
# View features for a date
cat data/cache/daily_features/features_2024-11-15.json
```

## Use Cases & Examples

### Example 1: Daily Operations

Run the pipeline every morning for today's date:

```bash
# Cron job (runs at 8am daily)
0 8 * * * cd /path/to/iterate-hackathon && python run_full_pipeline.py --use-real-data
```

### Example 2: Historical Analysis

Analyze events from the past:

```bash
# Analyze last week
for date in 2024-11-08 2024-11-09 2024-11-10 2024-11-11 2024-11-12; do
    python run_full_pipeline.py --date $date --use-real-data
done
```

### Example 3: Testing & Development

Quick testing without API costs:

```bash
# Demo mode
python run_full_pipeline.py --demo

# Or use integration test
python test_data_integration.py
```

### Example 4: Production Deployment

Full pipeline with all features:

```bash
# Build features for date range
python build_alert_features.py --start 2024-10-01 --end 2024-11-15

# Run pipeline with real data + LLM
python run_full_pipeline.py --date 2024-11-15 --use-real-data
```

## Troubleshooting

### "ANTHROPIC_API_KEY must be provided"

**Solution:** Set your API key in `.env`:

```bash
cp .env.example .env
# Edit .env and add your key
echo "ANTHROPIC_API_KEY=sk-ant-..." >> .env
```

### "Sales data not found"

**Solution:** Place your CSV files in the correct location:

```bash
mkdir -p data/input/Retail
# Copy your files:
# - retail_sales_data_*.csv
# - retail_inventory_snapshot_*.csv
```

Or run without `--use-real-data` flag (uses heuristic mode).

### "No events found for date"

**Possible causes:**
1. **No news fetched yet** - Run `python run_news_alerts.py` first
2. **No events detected** - News didn't contain relevant events
3. **Wrong date** - Check `data/events/` for available dates

**Solution:**

```bash
# Generate demo events
python run_news_alerts.py --demo

# Or fetch real news
python run_news_alerts.py --max-articles 50
```

### "ModuleNotFoundError: No module named 'pandas'"

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

## Performance & Costs

### Execution Time

| Mode | Time | Cost |
|------|------|------|
| Demo | ~5 seconds | $0 |
| Heuristic (50 articles) | ~2 minutes | ~$1.50 |
| Data-driven (50 articles) | ~3 minutes | ~$1.50 |
| Data-driven + LLM (50 articles, 10 alerts) | ~4 minutes | ~$1.60 |

### API Costs (Approximate)

**Event Detection (Agent 1):**
- ~$0.03 per article analyzed
- 50 articles = ~$1.50

**Context Matching (Agent 2):**
- Rules only = $0
- Rules + LLM = ~$0.01 per alert

**Monthly Estimates:**

| Scenario | Articles/day | Alerts/day | Monthly Cost |
|----------|--------------|------------|--------------|
| Light | 20 | 5 | ~$19 |
| Medium | 50 | 10 | ~$48 |
| Heavy | 100 | 20 | ~$96 |

## Architecture Summary

### Two-Agent Design

**Agent 1: Event Detector**
- **Input:** News articles
- **Process:** Claude Sonnet 4.5 extracts structured events
- **Output:** Detected events (JSON)
- **Role:** Fact extraction, NO predictions

**Agent 2: Context Matcher**
- **Input:** Detected events + Business data (optional)
- **Process:** Rule-based matching + Optional LLM enhancement
- **Output:** Business alerts with playbooks
- **Role:** Binary YES/NO decisions, actionable recommendations

### Data Flow

```
News Sources → Event Detector → Detected Events
                                      ↓
Business Data → Context Matcher → Business Alerts
```

## Next Steps

1. **Get Started:**
   ```bash
   python run_full_pipeline.py --demo
   ```

2. **Add API Key:**
   ```bash
   cp .env.example .env
   # Edit .env
   ```

3. **Run Production:**
   ```bash
   python run_full_pipeline.py --date 2024-11-15 --use-real-data
   ```

4. **Review Outputs:**
   ```bash
   cat data/alerts/daily_report_2024-11-15.json
   ```

## Additional Resources

- **Context Matcher Guide:** `CONTEXT_MATCHER_GUIDE.md`
- **Quick Start:** `NEWS_ALERTS_QUICKSTART.md`
- **Developer Guide:** `DEVELOPER_GUIDE_ALERT_FEATURES.md`
- **Architecture:** `NEWS_ALERTS_REFOCUSED.md`
