# Context Matcher Guide

Complete guide to the Context Matcher (Agent 2) in the News Alerts system.

## Overview

The Context Matcher is the second agent in our two-agent architecture:

```
┌─────────────────┐       ┌──────────────────┐       ┌─────────────────┐
│  News Sources   │──────▶│ Event Detector   │──────▶│ Detected Events │
└─────────────────┘       │   (Agent 1)      │       │    (JSON)       │
                          └──────────────────┘       └─────────────────┘
                                                              │
                                                              ▼
                          ┌──────────────────┐       ┌─────────────────┐
                          │ Context Matcher  │◀──────│ Business Data   │
                          │   (Agent 2)      │       │  (Inventory,    │
                          └──────────────────┘       │   Sales, etc.)  │
                                  │                  └─────────────────┘
                                  ▼
                          ┌──────────────────┐
                          │ Business Alerts  │
                          │  + Playbooks     │
                          └──────────────────┘
```

### Key Principle: **NO LLM, Pure Business Logic**

The Context Matcher uses **deterministic business rules** (not AI) to:
- Match detected events against business context
- Make binary YES/NO decisions on alerts
- Map to pre-defined action playbooks
- Generate actionable recommendations

## Architecture

### Components Built

1. **playbooks.py** - Action templates for different alert types
2. **alert_models.py** - Pydantic models for alerts and decisions
3. **context_matcher.py** - Business logic for event evaluation
4. **run_context_matcher.py** - CLI script

### How It Works

```python
# 1. Load detected events
events = event_storage.load_events(date.today())

# 2. Initialize matcher with business rules (and optional LLM)
matcher = ContextMatcher(enhance_with_llm=True)

# 3. Evaluate each event
for event in events:
    # Rule-based decision (fast, deterministic)
    alert = matcher.evaluate_single_event(event)

    # LLM enhancement (rich explanations)
    if alert:
        # Alert now includes:
        # - Rule-based decision (YES/NO)
        # - LLM business impact analysis
        # - Enhanced recommendations
        # - Manager talking points
        execute_alert(alert)
```

### LLM Enhancements (NEW)

The Context Matcher now supports **optional LLM enhancements** for richer alerts:

**Hybrid Approach:**
- **Rules decide** → Fast, cheap, deterministic ($0 cost)
- **LLM explains** → Rich insights, natural language (~$0.01/alert)

**What LLM Adds:**
1. **Business Impact Summary** - Natural language explanation
2. **Enhanced Actions** - Specific product recommendations, execution tips
3. **Risk Assessment** - What could go wrong, opportunities, timeline
4. **Manager Talking Points** - Ready-to-use team briefing

**Cost Comparison:**
```
Rules Only:        $0 per alert (instant)
Rules + LLM:       ~$0.01 per alert (1-2 seconds)

10 alerts/day:     $0.30/month with LLM vs. $0 without
100 alerts/day:    $3/month with LLM vs. $0 without
```

**Enable/Disable:**
```python
# With LLM (default - richer alerts)
matcher = ContextMatcher(enhance_with_llm=True)

# Rules only (faster, cheaper)
matcher = ContextMatcher(enhance_with_llm=False)
```

### Data-Driven Matching (NEW)

The Context Matcher now supports **data-driven decision making** using real business data from the alert_features pipeline:

**Heuristic vs. Data-Driven:**

| Mode | How It Works | Data Requirements | Accuracy |
|------|--------------|-------------------|----------|
| **Heuristic** | Keyword matching + severity thresholds | None | Good |
| **Data-Driven** | Real inventory + consumption + traffic patterns | Sales & inventory CSV files | Excellent |

**What Data-Driven Adds:**

For **Health Emergencies:**
- ✅ Actual inventory levels (not guesses)
- ✅ Real consumption rates (normal vs outbreak)
- ✅ Days of supply calculations (4.5x outbreak multiplier)
- ✅ Supplier information with lead times
- ✅ Location-specific stock breakdowns

Example decision logic:
```python
# Heuristic mode:
if event.severity == "high":
    generate_alert()  # Generic alert

# Data-driven mode:
features = calculator.get_health_emergency_features(
    category="OTC : GIT",
    as_of_date=today
)

if features['inventory_health']['days_of_supply_outbreak'] < 5:
    generate_alert(
        reason=f"CRITICAL: Only {days} days at outbreak rate",
        confidence=0.95,  # High confidence with real data
        supplier_contacts=features['suppliers']
    )
```

For **Major Events:**
- ✅ Historical traffic baselines per location
- ✅ Peak capacity patterns
- ✅ Event-relevant category inventory
- ✅ Traffic impact estimates (historical 80% lift)
- ✅ Product-level stock availability

**Enable/Disable:**
```python
# Heuristic-based (default, no data files needed)
matcher = ContextMatcher(use_real_data=False)

# Data-driven (requires sales + inventory CSV files)
matcher = ContextMatcher(use_real_data=True)
```

**Data Requirements:**

Place these files in your project:
```
data/
  input/
    Retail/
      retail_sales_data_01_09_2023_to_31_10_2025.csv
      retail_inventory_snapshot_30_10_25.csv
```

If files not found, system **gracefully falls back** to heuristic mode with a warning.

**CLI Usage:**
```bash
# Heuristic mode (no data needed)
python run_context_matcher.py

# Data-driven mode (uses real business data)
python run_context_matcher.py --use-real-data

# Data-driven + LLM enhancements (best of both worlds)
python run_context_matcher.py --use-real-data

# Data-driven only, no LLM (fast + accurate)
python run_context_matcher.py --use-real-data --no-llm
```

## Usage

### Basic Usage

```bash
# Process today's events with LLM enhancements (default)
python run_context_matcher.py

# Rules only (faster, cheaper, deterministic)
python run_context_matcher.py --no-llm

# Process specific date
python run_context_matcher.py --date 2024-11-15

# View statistics
python run_context_matcher.py --stats
```

### End-to-End Pipeline

```bash
# Step 1: Detect events from news
python run_news_alerts.py --max-articles 10

# Step 2: Generate business alerts from detected events
python run_context_matcher.py
```

## Business Logic

### Health Emergency Evaluation

**Decision Rules:**

1. **Product Relevance Check**
   ```python
   if event mentions ["flu", "cold", "virus"]:
       affected_categories = ["OTC : Cold & Flu"]
       alert_needed = True
   ```

2. **Severity Assessment**
   ```python
   if event.severity in ["high", "critical"]:
       playbook = "health_emergency_critical"
       urgency = "immediate"
   else:
       playbook = "health_emergency_moderate"
       urgency = "within_24h"
   ```

3. **Location Check**
   ```python
   if "dublin" in event.location or "ireland" in event.location:
       all_stores_affected = True
       confidence += 0.1
   ```

4. **Final Decision**
   ```python
   if alert_needed and affected_categories:
       generate_alert(playbook, affected_categories)
   ```

### Major Event Evaluation

**Decision Rules:**

1. **Attendance Assessment**
   ```python
   if attendance >= 10,000:
       impact = "high"
       playbook = "major_event_high_impact"
   elif attendance >= 5,000:
       impact = "moderate"
       playbook = "major_event_moderate_impact"
   ```

2. **Proximity Check**
   ```python
   if event_location in ["3Arena", "Croke Park", "Aviva Stadium"]:
       nearby_stores = get_stores_within_1km(event_location)
       alert_needed = True
   ```

3. **Timing Assessment**
   ```python
   days_until_event = (event_date - today).days
   if days_until_event <= 7:
       urgency = "within_week"
   ```

## Playbooks

Playbooks contain pre-defined action plans for different alert scenarios.

### Health Emergency - Critical

**Actions:**
1. ✅ **Immediate** - Review inventory levels (15 min, Pharmacy Manager)
2. ✅ **Immediate** - Calculate days-of-supply at 2-3x demand (30 min, Inventory Team)
3. ✅ **Immediate** - Emergency orders for <7 days supply (1 hour, Inventory Team)
4. ✅ **Today** - Contact suppliers (1 hour, Pharmacy Manager)
5. ✅ **Today** - Set up displays (30 min, All Staff)
6. ✅ **This Week** - Monitor trends daily (ongoing, Inventory Team)

**Success Criteria:**
- No stockouts of critical products
- Maintained >5 days supply
- Sales captured >80% of estimated demand

### Major Event - High Impact

**Actions:**
1. ✅ **Today** - Review store proximity (15 min, Pharmacy Manager)
2. ✅ **Today** - Increase convenience inventory (1 hour, Inventory Team)
3. ✅ **Today** - Ensure adequate staffing (30 min, Pharmacy Manager)
4. ✅ **This Week** - Promotional displays (1 hour, All Staff)
5. ✅ **This Week** - Consider extended hours (planning, Pharmacy Manager)

**Success Criteria:**
- No stockouts during event
- Transaction times <5 min average
- Sales lift >20% vs normal

## Output Files

### Alert Storage

Alerts are saved to `data/alerts/`:

```
data/alerts/
├── alert_2024-11-15_a1b2c3d4.json          # Individual alert
├── alert_2024-11-15_e5f6g7h8.json
└── daily_report_2024-11-15.json            # Summary report
```

### Alert Structure

```json
{
  "alert_id": "uuid",
  "alert_type": "health_emergency",
  "severity": "critical",
  "urgency": "immediate",
  "event_title": "Norovirus Outbreak in Dublin",
  "decision": {
    "alert_needed": true,
    "confidence": 0.85,
    "reasoning": [
      "We stock relevant products: OTC : GIT, Hand Sanitizer",
      "High severity event: critical",
      "Event in our market area: Dublin"
    ]
  },
  "immediate_actions": [
    "Review current inventory levels for affected OTC categories",
    "Calculate days-of-supply at elevated demand (2-3x normal)"
  ],
  "playbook_name": "Health Emergency - Critical Response"
}
```

## Example Output

```
================================================================================
CONTEXT MATCHER - Business Alert Generation
================================================================================
Date: 2024-11-15

Initializing Context Matcher...

Evaluating events for 2024-11-15...
Evaluating 3 detected events...

================================================================================
MATCHING RESULTS
================================================================================
Alerts Generated: 2

Alerts by Severity:
  critical: 1
  moderate: 1

Alerts by Type:
  health_emergency: 1
  major_event: 1

================================================================================
GENERATED ALERTS
================================================================================

ALERT 1/2
================================================================================
ALERT: Listeriosis Outbreak in Dublin
================================================================================
Type: HEALTH_EMERGENCY | Severity: CRITICAL | Urgency: immediate
Generated: 2024-11-15T14:30:00

EVENT DETAILS:
  Health officials investigating listeriosis outbreak affecting older adults
  Location: Dublin
  Date: 2024-11-15

BUSINESS IMPACT:
  Estimated Impact: HIGH
  Affected Categories: OTC : GIT, Hand Sanitizer
  Affected Locations: Baggot St, Grafton St, O'Connell St

DECISION RATIONALE:
  • We stock relevant products: OTC : GIT, Hand Sanitizer
  • High severity event: critical
  • Immediate response required
  • Event in our market area: Dublin
  Confidence: 95%

IMMEDIATE ACTIONS:
  1. Review current inventory levels for affected OTC categories (Est. time: 15 minutes, Owner: pharmacy_manager)
  2. Calculate days-of-supply at elevated demand (2-3x normal) (Est. time: 30 minutes, Owner: inventory_team)
  3. Place emergency orders for products with <7 days supply at elevated demand (Est. time: 1 hour, Owner: inventory_team)

SHORT-TERM ACTIONS:
  1. Contact key suppliers to confirm stock availability and expedited delivery (Est. time: 1 hour, Owner: pharmacy_manager)
  2. Set up prominent in-store displays for relevant health products (Est. time: 30 minutes, Owner: all_staff)
  3. Brief staff on symptoms, recommended products, and customer guidance (Est. time: 15 minutes, Owner: pharmacy_manager)

MONITORING PLAN:
  • Daily sales by affected category
  • Stock levels (units and days-of-supply)
  • Supplier delivery times
  • Customer inquiries/complaints

Playbook: Health Emergency - Critical Response
Alert ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890
================================================================================
```

## Integration with Business Data

### Current State (MVP)

The Context Matcher currently uses **heuristic-based logic** without requiring live business data:

```python
# Simplified decision making
if "flu" in event.description.lower():
    affected_categories = ["OTC : Cold & Flu"]
    alert_needed = True
```

### Future Integration (Production)

Connect to real business data sources:

```python
from alert_features import AlertFeatureCalculator

# Load real inventory data
calculator = AlertFeatureCalculator(sales_df, inventory_df)

# Get actual inventory levels
health_features = calculator.get_health_emergency_features(
    category="OTC : Cold & Flu",
    as_of_date=date.today()
)

# Make data-driven decision
if health_features['days_of_supply'] < 7:
    alert_needed = True
    urgency = "immediate"
```

## Configuration

Edit business rules in `context_matcher.py`:

```python
self.config = {
    # Your product categories
    "health_emergency_categories": [
        "OTC : Cold & Flu",
        "OTC : Analgesics",
        # Add your categories
    ],

    # Your store locations
    "store_locations": [
        {"name": "Your Store", "lat": 53.33, "lon": -6.24}
    ],

    # Distance thresholds (km)
    "proximity_thresholds": {
        "high_impact": 1.0,
        "moderate_impact": 3.0
    },

    # Attendance thresholds
    "event_attendance_thresholds": {
        "high_impact": 10000,
        "moderate_impact": 5000
    }
}
```

## Extending the System

### Add New Event Type

1. **Create playbook** in `playbooks.py`:
   ```python
   WEATHER_EXTREME_PLAYBOOK = Playbook(...)
   ```

2. **Add evaluation logic** in `context_matcher.py`:
   ```python
   def _evaluate_weather_extreme(self, event):
       # Your business rules
       if event.severity == "high":
           return create_alert(...)
   ```

3. **Update routing** in `evaluate_single_event()`:
   ```python
   elif event.event_type == "weather_extreme":
       return self._evaluate_weather_extreme(event)
   ```

### Customize Playbooks

Edit `playbooks.py` to match your business processes:

```python
PlaybookAction(
    priority="immediate",
    action="Your custom action",
    responsible="your_role",
    estimated_time="30 minutes"
)
```

## Testing

### Test with Sample Data

```bash
# 1. Run event detector in demo mode
python run_news_alerts.py --demo

# 2. Run context matcher
python run_context_matcher.py
```

### Test with Real Events

```bash
# 1. Detect events from real news
python run_news_alerts.py --max-articles 10

# 2. Generate alerts
python run_context_matcher.py

# 3. Review alerts
ls data/alerts/
cat data/alerts/daily_report_$(date +%Y-%m-%d).json
```

## Troubleshooting

### "No events found"

**Cause:** No events detected for the date

**Solution:**
```bash
# Check if events exist
ls data/events/

# Run event detector first
python run_news_alerts.py --demo
```

### "No actionable alerts generated"

**Cause:** Events didn't meet alert criteria

**Possible reasons:**
- Events not in your product categories
- Events outside your geographic area
- Events below severity thresholds

**Solution:** Review business rules in `context_matcher.py`

### Alerts not actionable

**Cause:** Generic playbooks don't match your business

**Solution:** Customize playbooks in `playbooks.py` with your actual processes

## Best Practices

### 1. Review Alerts Daily

```bash
# Morning routine
python run_context_matcher.py
cat data/alerts/daily_report_$(date +%Y-%m-%d).json
```

### 2. Tune Decision Thresholds

Monitor false positives/negatives and adjust:

```python
# In context_matcher.py
if health_features['days_of_supply'] < 10:  # Was 7, too aggressive
    alert_needed = True
```

### 3. Customize Playbooks

Replace generic actions with your actual procedures:

```python
PlaybookAction(
    priority="immediate",
    action="Call our supplier John at SupplyCo (555-1234)",  # Specific
    responsible="sarah_inventory_manager",  # Real person
    estimated_time="10 minutes"  # Accurate estimate
)
```

### 4. Integrate with Systems

Connect to your actual tools:

- Email alerts to managers
- Slack notifications for urgent items
- Update inventory system automatically
- Create tasks in project management tool

## Performance

- **Processing time**: <1 second per event
- **No API costs**: Pure business logic (no LLM)
- **Deterministic**: Same inputs = same outputs
- **Scalable**: Can handle 1000s of events/day

## Next Steps

1. **Test the system**
   - Run with demo data
   - Validate alert quality
   - Adjust thresholds

2. **Customize for your business**
   - Update product categories
   - Add your store locations
   - Customize playbooks

3. **Integrate with business data**
   - Connect to inventory system
   - Load sales data
   - Use real metrics for decisions

4. **Automate**
   - Setup daily cron jobs
   - Add email notifications
   - Create dashboard

5. **Expand**
   - Add more event types
   - Create more sophisticated rules
   - Integrate with ERP/POS systems

## Summary

✅ **Context Matcher complete and ready to use**
- Pure business logic (no LLM costs)
- Deterministic alert generation
- Pre-defined action playbooks
- Extensible architecture

🎯 **Next:** Test with real events and customize for your business!
