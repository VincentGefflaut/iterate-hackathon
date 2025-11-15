# News Alerts System

Black swan event detection for retail pharmacy using LLM-based structured extraction.

## Overview

This system fetches news from multiple sources and uses Claude AI to detect events that could affect a retail pharmacy business. It focuses on **fact extraction only** - no predictions.

## Architecture

```
News Sources → News Fetcher → Event Detector (Claude) → Event Storage
                                      ↓
                            Structured Events (JSON)
```

## Components

### 1. News Fetcher (`news_fetcher.py`)

Fetches news from multiple sources:
- **NewsAPI.org** - 100 free requests/day (requires API key)
- **Google News RSS** - Unlimited, no API key needed
- **Met Éireann** - Irish weather alerts via RSS

### 2. Event Detector (`event_detector.py`)

Uses Claude 3.5 Sonnet with structured outputs to detect:
- **Health Emergency** - Outbreaks, disease alerts, food poisoning
- **Major Events** - Concerts, festivals, conferences, sporting events

### 3. Event Storage (`event_storage.py`)

Stores detected events as JSON files organized by date.

### 4. Models (`models.py`)

Pydantic models for structured data:
- `NewsArticle` - Raw news article
- `DetectedEvent` - Extracted event with structured fields
- `DailyEventReport` - Summary of daily detections

## Installation

Required packages:
```bash
pip install anthropic requests feedparser pydantic
```

Environment variables:
```bash
export ANTHROPIC_API_KEY="your-api-key"
export NEWS_API_KEY="your-newsapi-key"  # Optional
```

## Usage

### Run Full Pipeline

```bash
# Detect all event types (health + major events)
python run_news_alerts.py

# Only health emergencies
python run_news_alerts.py --health-only

# Only major events
python run_news_alerts.py --events-only
```

### Demo Mode

Test with sample articles:
```bash
python run_news_alerts.py --demo
```

### View Statistics

```bash
python run_news_alerts.py --stats
```

## Output

Detected events are stored in `data/events/`:

```
data/events/
├── events_2024-11-15.json     # Events detected on this date
├── report_2024-11-15.json     # Daily summary report
└── ...
```

### Example Detected Event

```json
{
  "event_type": "health_emergency",
  "title": "Norovirus Outbreak in Dublin Hospitals",
  "description": "Health officials confirm 80+ cases across 3 hospitals",
  "severity": "high",
  "confidence": "high",
  "urgency": "immediate",
  "location": "Dublin",
  "event_date": "2024-11-15",
  "key_facts": [
    "80+ confirmed cases",
    "Affecting St. James's, Beaumont, and Mater hospitals",
    "HSE advises increased hygiene measures"
  ],
  "potential_relevance": "Health emergency affecting Dublin area. Demand for OTC anti-nausea and hygiene products may increase.",
  "source_url": "https://...",
  "published_at": "2024-11-15T10:00:00Z"
}
```

## Event Types Detected

Currently supports 2 event types:

### 1. Health Emergency
- Disease outbreaks (flu, norovirus, etc.)
- Food poisoning incidents
- Air quality warnings
- Health alerts

**Extracts:**
- What disease/condition
- Where (location)
- Severity level
- Affected areas

### 2. Major Events
- Concerts (3Arena, etc.)
- Sporting events (Croke Park, Aviva Stadium)
- Festivals
- Conferences

**Extracts:**
- Event name
- Date(s)
- Location/venue
- Expected attendance

## Next Steps

### Phase 2: Context Matcher

Build the Context Matcher agent that:
1. Loads detected events
2. Matches against business data (from alert_features)
3. Generates binary YES/NO alerts
4. Triggers pre-defined playbooks

### Phase 3: Additional Event Types

Expand to detect:
- Weather Extreme
- Competitor Actions
- Supply Disruptions
- Regulatory Changes
- Economic Shocks
- Viral Trends

## Performance

- News fetching: ~2-5 seconds for 50-100 articles
- Event detection: ~1-2 seconds per article (Claude API)
- Total pipeline: ~2-5 minutes for 100 articles

## Troubleshooting

### No articles found
- Check internet connection
- NewsAPI key may be invalid or at limit
- Google News RSS may be blocked in some regions

### Event detection errors
- Verify ANTHROPIC_API_KEY is set
- Check API quota/limits
- Review article content quality

### Storage errors
- Ensure `data/events/` directory exists
- Check write permissions

## Files

```
news_alerts/
├── __init__.py           # Package initialization
├── models.py             # Pydantic models
├── news_fetcher.py       # News fetching logic
├── event_detector.py     # Claude integration
├── event_storage.py      # Event storage
└── README.md             # This file
```

## References

- Architecture: `NEWS_ALERTS_REFOCUSED.md`
- Feature engineering: `DEVELOPER_GUIDE_ALERT_FEATURES.md`
- Anthropic API: https://docs.anthropic.com/
- NewsAPI: https://newsapi.org/
