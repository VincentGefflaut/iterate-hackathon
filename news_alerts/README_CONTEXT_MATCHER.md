# news_alerts Package - Complete System

Two-agent black swan event detection and alert generation system for retail pharmacy.

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        NEWS SOURCES                               │
│  NewsAPI | Google News RSS | Met Éireann | Custom RSS            │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                   AGENT 1: EVENT DETECTOR                         │
│                                                                   │
│  • Fetches news articles                                         │
│  • Uses Claude AI (LLM) to extract structured events            │
│  • Classifies: health_emergency, major_event, etc.              │
│  • Extracts facts only (NO predictions)                         │
│                                                                   │
│  Output: DetectedEvent (JSON)                                   │
└───────────────────────┬──────────────────────────────────────────┘
                        │
                        ▼
┌──────────────────────────────────────────────────────────────────┐
│                   AGENT 2: CONTEXT MATCHER                        │
│                                                                   │
│  • Loads detected events                                         │
│  • Applies business rules (NO LLM)                              │
│  • Matches against business data (inventory, sales, location)   │
│  • Makes binary YES/NO alert decisions                          │
│  • Maps to pre-defined playbooks                                │
│                                                                   │
│  Output: BusinessAlert + Playbook Actions                       │
└──────────────────────────────────────────────────────────────────┘
```

## Modules

### Event Detection (Agent 1)

| Module | Description |
|--------|-------------|
| `models.py` | Pydantic models for events |
| `news_fetcher.py` | Multi-source news fetching |
| `event_detector.py` | Claude AI integration |
| `event_storage.py` | Event persistence |

**CLI:** `run_news_alerts.py`

### Context Matching (Agent 2)

| Module | Description |
|--------|-------------|
| `alert_models.py` | Pydantic models for alerts |
| `playbooks.py` | Action templates |
| `context_matcher.py` | Business logic |

**CLI:** `run_context_matcher.py`

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env and add ANTHROPIC_API_KEY
```

### 3. Run Event Detector (Agent 1)

```bash
# Test with sample articles
python run_news_alerts.py --demo

# Process real news (10 articles, ~$0.03)
python run_news_alerts.py --max-articles 10
```

### 4. Run Context Matcher (Agent 2)

```bash
# Generate business alerts from detected events
python run_context_matcher.py
```

### 5. Review Alerts

```bash
# View today's alerts
cat data/alerts/daily_report_$(date +%Y-%m-%d).json

# List all alerts
ls data/alerts/
```

## Event Types Supported

### ✅ Fully Implemented

1. **Health Emergency**
   - Outbreaks, disease alerts, food poisoning
   - Maps to: OTC health products
   - Playbook: Inventory checks, emergency orders, staff briefing

2. **Major Events**
   - Concerts, festivals, conferences, sporting events
   - Maps to: Store proximity, foot traffic
   - Playbook: Staffing, convenience inventory, extended hours

### 🔜 Future Event Types

3. **Weather Extreme** - Heatwaves, storms, flooding
4. **Competitor Action** - New stores, promotions
5. **Supply Disruption** - Supplier issues, strikes
6. **Regulatory Change** - Drug reclassifications
7. **Economic Shock** - Market crashes, layoffs
8. **Viral Trend** - TikTok products, celebrity mentions

## Data Flow

### Input: News Articles

```json
{
  "title": "Norovirus Outbreak in Dublin Hospitals",
  "description": "Health officials report 80+ cases...",
  "url": "https://news.ie/article",
  "published_at": "2024-11-15T10:00:00Z"
}
```

### Agent 1 Output: Detected Event

```json
{
  "event_type": "health_emergency",
  "title": "Norovirus Outbreak in Dublin",
  "severity": "high",
  "confidence": "high",
  "urgency": "immediate",
  "location": "Dublin",
  "key_facts": [
    "80+ confirmed cases",
    "Multiple hospitals affected"
  ],
  "potential_relevance": "Demand for OTC anti-nausea products may increase"
}
```

### Agent 2 Output: Business Alert

```json
{
  "alert_type": "health_emergency",
  "severity": "critical",
  "urgency": "immediate",
  "decision": {
    "alert_needed": true,
    "confidence": 0.85,
    "reasoning": [
      "We stock relevant products: OTC : GIT",
      "High severity event",
      "Event in our market area"
    ]
  },
  "immediate_actions": [
    "Review inventory levels for OTC : GIT products",
    "Calculate days-of-supply at 2-3x normal demand",
    "Place emergency orders if <7 days supply"
  ],
  "playbook_name": "Health Emergency - Critical Response"
}
```

## API Reference

### Event Detector

```python
from news_alerts import EventDetectorAgent, NewsFetcher, EventStorage

# Fetch news
fetcher = NewsFetcher()
articles = fetcher.fetch_irish_health_news()

# Detect events
detector = EventDetectorAgent()
for article in articles:
    result = detector.detect_event(article, event_types=["health_emergency"])
    if result.detected_event:
        storage.save_event(result.detected_event)
```

### Context Matcher

```python
from news_alerts import ContextMatcher

# Initialize matcher
matcher = ContextMatcher()

# Evaluate events and generate alerts
alerts = matcher.evaluate_events(date.today())

# Process alerts
for alert in alerts:
    if alert.severity == "critical":
        send_urgent_notification(alert)
        execute_playbook(alert.immediate_actions)
```

### Playbooks

```python
from news_alerts import get_playbook

# Get playbook for health emergency
playbook = get_playbook("health_emergency", "critical")

print(f"Playbook: {playbook.name}")
for action in playbook.actions:
    print(f"  [{action.priority}] {action.action}")
```

## Configuration

### Business Rules (context_matcher.py)

```python
self.config = {
    # Product categories
    "health_emergency_categories": [
        "OTC : Cold & Flu",
        "OTC : Analgesics",
        # Add your categories
    ],

    # Store locations
    "store_locations": [
        {"name": "Baggot St", "lat": 53.3314, "lon": -6.2462}
    ],

    # Thresholds
    "proximity_thresholds": {"high_impact": 1.0},  # km
    "event_attendance_thresholds": {"high_impact": 10000}
}
```

### Playbooks (playbooks.py)

```python
PlaybookAction(
    priority="immediate",  # immediate, today, this_week
    action="Your action description",
    responsible="role_or_person",
    estimated_time="30 minutes"
)
```

## Output Files

```
data/
├── events/                              # Agent 1 output
│   ├── events_2024-11-15.json         # Detected events
│   └── report_2024-11-15.json         # Detection summary
│
└── alerts/                              # Agent 2 output
    ├── alert_2024-11-15_abc123.json   # Individual alerts
    └── daily_report_2024-11-15.json   # Alert summary
```

## Cost Estimate

### Agent 1: Event Detector
- Uses Claude AI: ~$0.003 per article
- 50 articles/day: ~$0.15/day = $4.50/month
- Configurable with `--max-articles`

### Agent 2: Context Matcher
- Pure business logic: **$0 API costs**
- Unlimited events processing
- Deterministic decisions

## Testing

```bash
# End-to-end test
python run_news_alerts.py --demo           # Detect events
python run_context_matcher.py             # Generate alerts

# Check outputs
cat data/events/events_*.json
cat data/alerts/daily_report_*.json
```

## Integration Points

### Future Enhancements

1. **Real Business Data** (from alert_features module)
   ```python
   from alert_features import AlertFeatureCalculator
   features = calculator.get_health_emergency_features(...)
   ```

2. **Email Notifications**
   ```python
   if alert.severity == "critical":
       send_email(to="manager@pharmacy.ie", alert=alert)
   ```

3. **Dashboard**
   ```python
   streamlit run dashboard.py
   ```

4. **Automated Actions**
   ```python
   if alert.urgency == "immediate":
       create_purchase_order(products=alert.affected_categories)
   ```

## Troubleshooting

### No events detected

**Cause:** No relevant news articles found

**Solution:**
```bash
# Check news sources
python -c "from news_alerts import NewsFetcher; f = NewsFetcher(); print(len(f.fetch_irish_health_news()))"

# Use demo mode
python run_news_alerts.py --demo
```

### No alerts generated

**Cause:** Events didn't meet business criteria

**Solution:** Review and adjust thresholds in `context_matcher.py`

### Wrong alert severity

**Cause:** Business rules need tuning

**Solution:** Customize decision logic in `_evaluate_health_emergency()` or `_evaluate_major_event()`

## Extending

### Add New Event Type

1. Update `event_detector.py` prompts
2. Create playbook in `playbooks.py`
3. Add evaluation method in `context_matcher.py`
4. Test with sample events

### Connect Real Data

Replace heuristics with actual business data:

```python
# Before (heuristic)
if "flu" in event.description:
    alert_needed = True

# After (data-driven)
if inventory["OTC : Cold & Flu"]["days_supply"] < 7:
    alert_needed = True
```

## Support

- Quick Start: See [NEWS_ALERTS_QUICKSTART.md](../NEWS_ALERTS_QUICKSTART.md)
- Setup Guide: See [SETUP.md](../SETUP.md)
- Context Matcher: See [CONTEXT_MATCHER_GUIDE.md](../CONTEXT_MATCHER_GUIDE.md)

## Version History

- **v0.2.0** - Added Context Matcher (Agent 2)
- **v0.1.0** - Initial Event Detector (Agent 1)
