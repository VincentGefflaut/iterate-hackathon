# Developer Guide: Alert Features Data Engineering

## Table of Contents
- [What's Implemented](#whats-implemented)
- [Architecture Overview](#architecture-overview)
- [Module Documentation](#module-documentation)
- [Quick Start Guide](#quick-start-guide)
- [Next Steps](#next-steps)
- [Integration Roadmap](#integration-roadmap)

---

## What's Implemented

### ✅ Core Components

1. **Daily Aggregation System** (`alert_features/daily_aggregator.py`)
   - Aggregates raw sales data into daily metrics
   - Calculates totals (revenue, units, transactions)
   - Groups by category (80+ categories tracked)
   - Groups by location (10 locations tracked)
   - Groups by supplier (major suppliers only)
   - Growth calculations (vs yesterday, vs last year)
   - Historical context (7-day, 30-day averages)

2. **Alert-Specific Feature Calculators** (`alert_features/alert_features.py`)
   - **Major Events**: Location traffic baselines, event-relevant categories, inventory buffers
   - **Health Emergency**: Category demand profiles, seasonal peaks, days-of-supply calculations
   - **Weather Extreme**: Seasonal patterns, weather-to-product mappings, stock adequacy
   - **Supply Disruption**: Supplier criticality rankings, days-of-supply by supplier, alternative supplier identification
   - **Viral Trend**: Product search, stock levels, viral spike capacity estimation

3. **Anomaly Detection** (`alert_features/anomaly_detector.py`)
   - Z-score based anomaly detection
   - Baseline calculation (mean, std, percentiles)
   - Category-level anomaly detection
   - Location-level anomaly detection
   - Multidimensional anomaly validation (reduces false positives)
   - Surge/drought detection (2x above/below normal)
   - Human-readable anomaly reports

4. **Feature Caching** (`alert_features/feature_cache.py`)
   - JSON-based feature storage
   - Fast read/write operations
   - Cache statistics and management
   - CSV export for analysis
   - Automatic cleanup of old files

5. **Pipeline Orchestrator** (`build_alert_features.py`)
   - Command-line interface for feature building
   - Single date or date range processing
   - Demo mode showing all alert features
   - Cache statistics viewer
   - CSV export functionality

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                               │
│  Raw Sales (1.3M records) + Inventory (824K records)            │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DAILY AGGREGATOR                              │
│  • Aggregates by day, category, location, supplier              │
│  • Calculates growth rates (YoY, DoD)                           │
│  • Adds historical context (7d, 30d, YoY)                       │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ANOMALY DETECTOR                               │
│  • Calculates baselines (mean, std)                             │
│  • Detects z-score anomalies                                    │
│  • Validates multidimensional patterns                          │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FEATURE CACHE                                 │
│  • Stores as JSON (data/cache/daily_features/*.json)            │
│  • Fast retrieval (<100ms)                                      │
│  • Baselines stored separately                                  │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ALERT FEATURE CALCULATOR                            │
│  • On-demand alert-specific features                            │
│  • Major Events, Health Emergency, Weather, etc.                │
│  • Uses cached daily features + raw data                        │
└────────────────────┬─────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│              ALERT SYSTEM (Future Integration)                   │
│  • Event Detector (LLM)                                         │
│  • Context Matcher (uses features)                              │
│  • Alert Generator                                              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module Documentation

### 1. `DailyAggregator`

**Purpose**: Transform raw sales into daily aggregated features

**Key Methods**:
```python
from alert_features import DailyAggregator

aggregator = DailyAggregator(sales_df, inventory_df)

# Aggregate single day
features = aggregator.aggregate_day(date(2024, 10, 15))

# Aggregate date range
features_list = aggregator.aggregate_date_range(
    start_date=date(2024, 10, 1),
    end_date=date(2024, 10, 31)
)

# Get category baseline
baseline = aggregator.get_category_baseline(
    category="OTC : Cold & Flu",
    end_date=date(2024, 10, 15),
    window_days=30
)

# Get location baseline
baseline = aggregator.get_location_baseline(
    location="Baggot St",
    end_date=date(2024, 10, 15),
    window_days=30
)
```

**Output Structure**:
```json
{
  "date": "2024-10-15",
  "daily_totals": {
    "total_revenue": 45230.50,
    "total_units": 1250,
    "transaction_count": 890
  },
  "by_category": {
    "OTC : Cold & Flu": {
      "revenue": 3450.25,
      "units": 210,
      "growth_vs_yesterday": 5.2,
      "growth_vs_last_year": 12.3
    }
  },
  "by_location": {...},
  "by_supplier": {...},
  "historical_context": {...}
}
```

### 2. `AlertFeatureCalculator`

**Purpose**: Calculate specialized features for each alert type

**Key Methods**:

```python
from alert_features import AlertFeatureCalculator

calc = AlertFeatureCalculator(sales_df, inventory_df)

# Major Events
major_event = calc.get_major_event_features("Baggot St", date(2024, 10, 15))
# Returns: traffic baseline, event-relevant categories, inventory

# Health Emergency
health = calc.get_health_emergency_features("OTC : Cold & Flu", date(2024, 10, 15))
# Returns: demand baseline, peaks, days-of-supply, suppliers

# Weather Extreme
weather = calc.get_weather_features("heatwave", date(2024, 10, 15))
# Returns: seasonal patterns, stock adequacy

# Supply Disruption
supply = calc.get_supply_disruption_features(date(2024, 10, 15))
# Returns: supplier criticality, resilience metrics

# Viral Trend
viral = calc.get_viral_trend_features("weight", date(2024, 10, 15))
# Returns: matching products, stock levels, spike capacity
```

### 3. `AnomalyDetector`

**Purpose**: Detect unusual patterns using statistical methods

**Key Methods**:

```python
from alert_features import AnomalyDetector

detector = AnomalyDetector(baseline_window_days=30)

# Calculate baselines
baselines = detector.calculate_baselines(
    sales_df,
    end_date=date(2024, 10, 15),
    window_days=30
)

# Detect anomalies in daily features
anomalies = detector.detect_daily_anomalies(daily_features, baselines)

# Generate human-readable report
report = detector.generate_anomaly_report(anomalies)
print(report)
```

**Anomaly Classification**:
- `z > 3`: **critical_anomaly**
- `z > 2`: **significant_anomaly**
- `z > 1.5`: **minor_anomaly**
- `else`: **normal**

**Multidimensional Validation**:
True anomaly flagged when:
- 2+ categories are anomalous, OR
- 2+ locations are anomalous, OR
- Total revenue significant AND 1+ category/location

### 4. `FeatureCache`

**Purpose**: Fast storage/retrieval of features

**Key Methods**:

```python
from alert_features import FeatureCache

cache = FeatureCache()

# Save/load daily features
cache.save_daily_features(features, date(2024, 10, 15))
features = cache.load_daily_features(date(2024, 10, 15))

# Save/load baselines
cache.save_baselines(baselines)
baselines = cache.load_baselines()

# Check if cached
if cache.has_features(date(2024, 10, 15)):
    # Load from cache
    pass

# Get latest cached date
latest = cache.get_latest_cached_date()

# Export to CSV
cache.export_to_csv("output.csv")

# Cache management
cache.print_cache_stats()
cache.delete_old_cache(keep_days=90)
```

---

## Quick Start Guide

### Installation

No additional dependencies beyond what you already have:
- pandas
- numpy
- scipy

### Build Features for Yesterday

```bash
python build_alert_features.py
```

### Build Features for Specific Date

```bash
python build_alert_features.py --date 2024-10-15
```

### Build Features for Date Range

```bash
python build_alert_features.py --start 2024-10-01 --end 2024-10-31
```

### View Demo of All Alert Features

```bash
python build_alert_features.py --demo
```

**Output Example**:
```
================================================================================
DEMO: Alert-Specific Features
================================================================================

Using features from: 2024-10-15

--------------------------------------------------------------------------------
1. MAJOR EVENTS Features (for Baggot St)
--------------------------------------------------------------------------------

Traffic Baseline:
  Avg daily transactions: 209
  Peak day: 291
  Slowest day: 73

Event-relevant categories:
  OTC : Analgesics:
    Daily baseline: €271.42 (29.3 units)
  OTC : First Aid:
    Daily baseline: €125.25 (23.9 units)
  OTC : Cold & Flu:
    Daily baseline: €122.70 (16.0 units)

--------------------------------------------------------------------------------
2. HEALTH EMERGENCY Features (OTC : Cold & Flu)
--------------------------------------------------------------------------------

Demand Baseline:
  Daily avg: 99.3 units (€701.78)
  Historical peak: 190 units
  Outbreak estimate: 447 units

Inventory Health:
  Current stock: 4020 units
  Days of supply (normal): 40.5
  Days of supply (outbreak): 9.0
  ALERT NEEDED: False

Top Suppliers:
  Kenvue (McNeil Healthcare): 53.6% of category
  Pharmax: 22.0% of category
  Haleon (GSK): 10.1% of category
```

### View Cache Statistics

```bash
python build_alert_features.py --stats
```

### Export to CSV

```bash
python build_alert_features.py --export analysis.csv
```

---

## Next Steps

### Phase 1: Complete Data Engineering (Current)

**Status**: ✅ COMPLETE

- [x] Daily aggregation module
- [x] Alert-specific feature calculators
- [x] Anomaly detection system
- [x] Feature caching layer
- [x] Command-line interface
- [x] Demo with actual data

### Phase 2: Historical Backfill (Immediate Next)

**Goal**: Build features for past 12 months for baseline establishment

**Tasks**:
1. **Backfill Features** (1-2 days)
   ```bash
   # Build features for entire 2024
   python build_alert_features.py --start 2024-01-01 --end 2024-12-31
   ```
   - Will create ~365 JSON files
   - Total cache size: ~10-15 MB
   - Processing time: ~2-3 hours

2. **Validate Features**
   - Spot check random dates
   - Verify anomaly detection is working
   - Check supplier rankings make sense

3. **Export for Analysis**
   ```bash
   python build_alert_features.py --export 2024_features.csv
   ```
   - Analyze in Excel/Jupyter
   - Look for interesting patterns
   - Validate seasonality

### Phase 3: Production Scheduling (Week 1)

**Goal**: Automate daily feature generation

**Tasks**:
1. **Create Cron Job** (Linux/Mac) or **Task Scheduler** (Windows)
   ```bash
   # Run every day at 5:00 AM
   0 5 * * * cd /path/to/project && python build_alert_features.py
   ```

2. **Add Monitoring**
   - Email notification if job fails
   - Slack notification for anomalies
   - Log file rotation

3. **Error Handling**
   - Retry logic if data loading fails
   - Graceful handling of missing dates
   - Alert if cache grows too large

### Phase 4: News Alert Integration (Week 2)

**Goal**: Connect features to LLM alert system

**Tasks**:
1. **Build Event Detector Agent**
   - Use Claude API with structured outputs
   - Implement event types from NEWS_ALERTS_REFOCUSED.md
   - Extract: event_type, date, location, severity

2. **Build Context Matcher**
   ```python
   class ContextMatcher:
       def __init__(self, feature_cache):
           self.cache = feature_cache
           self.calculator = AlertFeatureCalculator(...)

       def evaluate_event(self, detected_event):
           # Load relevant features
           if detected_event.event_type == "health_emergency":
               features = self.calculator.get_health_emergency_features(
                   category=detected_event.category,
                   as_of_date=today
               )

               # Decision logic
               if features['inventory_health']['alert_needed']:
                   return Alert(
                       alert=True,
                       urgency='immediate',
                       playbook='HEALTH_EMERGENCY_PLAYBOOK'
                   )
   ```

3. **Integrate with News Sources**
   - NewsAPI.org (100 free requests/day)
   - Google News RSS
   - Met Éireann weather API
   - Run daily at 6:00 AM (after features built)

4. **Build Playbook System**
   - Define playbooks from NEWS_ALERTS_REFOCUSED.md
   - Map event types to playbooks
   - Generate actionable recommendations

### Phase 5: Dashboard/UI (Week 3-4)

**Goal**: Visualize features and alerts

**Options**:

**Option A: Streamlit Dashboard** (Fastest)
```python
import streamlit as st
from alert_features import FeatureCache

st.title("Daily Features Dashboard")

cache = FeatureCache()
latest = cache.get_latest_cached_date()
features = cache.load_daily_features(latest)

# Display metrics
col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"€{features['daily_totals']['total_revenue']:,.0f}")
col2.metric("Transactions", features['daily_totals']['transaction_count'])
col3.metric("Avg Ticket", f"€{features['daily_totals']['avg_ticket']:.2f}")

# Anomaly alerts
if features['anomalies']['has_anomaly']:
    st.error("⚠️ Anomalies Detected!")
    for cat in features['anomalies']['category_anomalies']:
        st.write(f"- {cat['category']}: {cat['classification']}")
```

**Option B: Jupyter Notebook** (Analysis-focused)
- Interactive exploration
- Matplotlib/Plotly visualizations
- Export to PDF reports

**Option C: Web Dashboard** (Production-ready)
- Flask/FastAPI backend
- React frontend
- Real-time updates
- User authentication

### Phase 6: Advanced Features (Month 2+)

**Enhancements**:

1. **Real-Time Updates**
   - Stream processing (instead of batch)
   - Detect intra-day spikes
   - Immediate viral trend detection

2. **Machine Learning**
   - Better anomaly detection (Isolation Forest, LSTM)
   - Demand forecasting
   - Churn prediction

3. **External Data Integration**
   - Weather API (actual temps vs forecast)
   - Social media trending (Twitter, TikTok)
   - Economic indicators (inflation, employment)

4. **Multi-Store Comparison**
   - Peer group analysis
   - Best-practice identification
   - Cross-store recommendations

---

## Integration Roadmap

### Immediate (This Week)

1. **Backfill Historical Features**
   ```bash
   python build_alert_features.py --start 2024-01-01 --end 2024-12-31
   ```

2. **Validate Output**
   - Check cache stats
   - Review anomaly reports
   - Export and analyze in Excel

3. **Document Learnings**
   - What categories are most volatile?
   - Which suppliers are most critical?
   - What's the typical anomaly rate?

### Short-Term (Next 2 Weeks)

1. **Setup Daily Cron Job**
2. **Build Simple Event Detector** (Claude API)
3. **Create 1-2 Playbooks** (e.g., Health Emergency)
4. **Test End-to-End Flow**:
   - News → Event Detection → Feature Lookup → Alert Decision

### Medium-Term (Next Month)

1. **Complete All 8 Event Types**
2. **Build Streamlit Dashboard**
3. **Add Monitoring/Alerting**
4. **User Training/Documentation**

### Long-Term (Month 2-3)

1. **Evaluate Performance** (are alerts useful?)
2. **Iterate on Thresholds** (reduce false positives)
3. **Add ML Enhancements**
4. **Scale to More Data Sources**

---

## File Structure

```
Track retail/
├── alert_features/                    # Main package
│   ├── __init__.py
│   ├── daily_aggregator.py           # Daily aggregation
│   ├── alert_features.py             # Alert-specific features
│   ├── anomaly_detector.py           # Anomaly detection
│   ├── feature_cache.py              # Caching layer
│   └── README.md                     # Package documentation
│
├── build_alert_features.py           # Main CLI script
│
├── data/
│   ├── input/
│   │   └── Retail/
│   │       ├── retail_sales_data_*.csv
│   │       └── retail_inventory_snapshot_*.csv
│   └── cache/
│       └── daily_features/           # Feature cache
│           ├── 2024-10-15.json
│           ├── ...
│           └── baselines.json
│
├── NEWS_ALERTS_REFOCUSED.md          # Alert system design
├── NEWS_ALERTS_DASHBOARD_DESIGN.md   # Dashboard design (old)
└── DEVELOPER_GUIDE_ALERT_FEATURES.md # This file
```

---

## Performance Notes

- **Daily aggregation**: ~30 seconds for single day
- **Historical backfill**: ~2-3 hours for full year
- **Feature loading**: <100ms from cache
- **Memory usage**: ~500MB during aggregation
- **Cache size**: ~40KB per day (~15MB per year)

---

## Troubleshooting

### "No data for date"
- Sales data may not cover that date
- Check date format (YYYY-MM-DD)

### "Missing baselines"
- Run baseline calculation first
- Ensure 30+ days of prior data

### Pandas warnings about SettingWithCopyWarning
- Harmless - can be suppressed with `.copy()`
- Does not affect results

### Slow performance
- Processing 1.3M records takes time
- Use caching - don't recalculate
- Consider sampling for development

---

## Support & Questions

For questions or issues:
1. Check `alert_features/README.md`
2. Review `NEWS_ALERTS_REFOCUSED.md` for context
3. Inspect cache files directly (they're JSON)
4. Run `--demo` to see feature examples

---

## Summary

**What Works Now**:
- ✅ Complete data engineering pipeline
- ✅ All 5 alert feature types implemented
- ✅ Anomaly detection working
- ✅ Feature caching operational
- ✅ Tested with actual data (1.3M records)

**What's Next**:
1. Backfill 12 months of features
2. Setup daily automation
3. Build Event Detector (Claude API)
4. Create Context Matcher
5. Deploy first alert type (e.g., Health Emergency)

**Timeline to Production Alert System**:
- Week 1: Backfill + Automation
- Week 2: Event Detector + Context Matcher
- Week 3: End-to-end testing
- Week 4: Production deployment (1-2 alert types)
- Month 2: Scale to all 8 alert types

The foundation is solid. Next step: turn on the alerts! 🚀
