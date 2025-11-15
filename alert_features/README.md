# Alert Features Data Engineering

This package provides data engineering capabilities for the news alert system. It transforms raw sales and inventory data into structured features needed for context-aware alert generation.

## Overview

The system consists of 4 main components:

1. **DailyAggregator** - Aggregates raw sales into daily metrics
2. **AlertFeatureCalculator** - Computes alert-specific features
3. **AnomalyDetector** - Detects unusual patterns
4. **FeatureCache** - Stores features for fast access

## Architecture

```
Raw Sales Data
    ↓
DailyAggregator
    ↓
Daily Features (revenue, units, by category, by location)
    ↓
AnomalyDetector
    ↓
Anomaly Flags (surges, droughts, multidimensional)
    ↓
FeatureCache (JSON files)
    ↓
Alert System (uses features for context matching)
```

## Quick Start

### 1. Build Daily Features

```bash
# Build features for yesterday
python build_alert_features.py

# Build for specific date
python build_alert_features.py --date 2024-10-15

# Build for date range
python build_alert_features.py --start 2024-10-01 --end 2024-10-31
```

### 2. View Cache Statistics

```bash
python build_alert_features.py --stats
```

### 3. See Demo of Alert Features

```bash
python build_alert_features.py --demo
```

### 4. Export to CSV

```bash
python build_alert_features.py --export output.csv
```

## Daily Features Output

For each day, the system calculates:

```json
{
  "date": "2024-10-15",
  "execution_time": "2024-10-16T02:15:30",

  "daily_totals": {
    "total_revenue": 45230.50,
    "total_units": 1250,
    "transaction_count": 890,
    "avg_ticket": 50.82
  },

  "by_category": {
    "OTC : Cold & Flu": {
      "revenue": 3450.25,
      "units": 210,
      "growth_vs_yesterday": 5.2,
      "growth_vs_last_year": 12.3
    }
  },

  "by_location": {
    "Baggot St": {
      "revenue": 8450.00,
      "traffic": 145,
      "avg_ticket": 58.28,
      "vs_network_avg": 8.5
    }
  },

  "anomalies": {
    "has_anomaly": true,
    "category_anomalies": [...],
    "is_true_anomaly": false
  },

  "historical_context": {
    "7_day_average": 41200.00,
    "30_day_average": 42100.00,
    "same_day_last_year": {
      "revenue": 38450.00
    }
  }
}
```

## Alert-Specific Features

### 1. Major Events (Concerts, Festivals)

```python
from alert_features import AlertFeatureCalculator

calc = AlertFeatureCalculator(sales_df, inventory_df)

features = calc.get_major_event_features(
    location="Baggot St",
    as_of_date=date(2024, 10, 15)
)

# Returns:
# - Location traffic baseline
# - Event-relevant product categories
# - Inventory buffer
# - Historical event lift patterns
```

### 2. Health Emergency (Flu, Norovirus)

```python
features = calc.get_health_emergency_features(
    category="OTC : Cold & Flu",
    as_of_date=date(2024, 10, 15)
)

# Returns:
# - Daily demand baseline
# - Seasonal peak patterns
# - Current inventory vs spike needs
# - Days of supply (normal vs outbreak)
# - Supplier information
```

### 3. Weather Extreme (Heatwave, Cold Snap)

```python
features = calc.get_weather_features(
    weather_type="heatwave",  # or "cold_snap", "flooding"
    as_of_date=date(2024, 10, 15)
)

# Returns:
# - Seasonal patterns by category
# - Peak month identification
# - Current stock vs seasonal demand
# - Days of supply estimates
```

### 4. Supply Disruption

```python
features = calc.get_supply_disruption_features(
    as_of_date=date(2024, 10, 15)
)

# Returns:
# - Supplier criticality rankings
# - Revenue dependency (% of business)
# - Days of supply by supplier
# - Critical products with low stock
```

### 5. Viral Trend

```python
features = calc.get_viral_trend_features(
    product_keyword="weight",  # Search for weight loss products
    as_of_date=date(2024, 10, 15)
)

# Returns:
# - Matching products
# - Current stock levels
# - Normal vs viral sales rates
# - Days of supply at different spike levels
# - Ability to capitalize on trend
```

## Anomaly Detection

The system uses z-score method to detect anomalies:

```python
from alert_features import AnomalyDetector

detector = AnomalyDetector()

# Calculate baselines (mean, std)
baselines = detector.calculate_baselines(
    sales_df,
    end_date=date(2024, 10, 15),
    window_days=30
)

# Detect anomalies in daily features
anomalies = detector.detect_daily_anomalies(
    daily_features,
    baselines
)

# Anomaly classification:
# - z > 3: critical_anomaly
# - z > 2: significant_anomaly
# - z > 1.5: minor_anomaly
# - else: normal
```

### Multidimensional Anomaly Detection

To reduce false positives, the system flags true anomalies only when:
- 2+ categories are anomalous, OR
- 2+ locations are anomalous, OR
- Total revenue is significant AND at least 1 category/location

## Feature Caching

Features are cached as JSON files for fast access:

```
data/cache/daily_features/
├── 2024-10-01.json
├── 2024-10-02.json
├── ...
└── baselines.json
```

### Using the Cache

```python
from alert_features import FeatureCache

cache = FeatureCache()

# Save features
cache.save_daily_features(features, date(2024, 10, 15))

# Load features
features = cache.load_daily_features(date(2024, 10, 15))

# Check if cached
if cache.has_features(date(2024, 10, 15)):
    features = cache.load_daily_features(date(2024, 10, 15))

# Get latest cached date
latest = cache.get_latest_cached_date()

# Export to CSV for analysis
cache.export_to_csv("analysis.csv")

# Clean old cache (>90 days)
cache.delete_old_cache(keep_days=90)
```

## Integration with Alert System

The alert system's **Context Matcher** uses these features to make decisions:

```python
# Example: Health Emergency alert
event = {
    'event_type': 'health_emergency',
    'category': 'OTC : Cold & Flu',
    'severity': 'high'
}

# Load relevant features
health_features = calc.get_health_emergency_features(
    "OTC : Cold & Flu",
    as_of_date=today
)

# Decision logic
if health_features['inventory_health']['days_of_supply_outbreak'] < 5:
    # Generate alert!
    alert = {
        'alert': True,
        'reason': f"Only {days_of_supply} days of supply at outbreak rate",
        'urgency': 'immediate',
        'playbook': 'HEALTH_EMERGENCY_PLAYBOOK'
    }
```

## Data Requirements

### Input Data

**Sales Data** (`retail_sales_data_*.csv`):
- Sale Date
- Sale ID
- Branch Name
- Dept Fullname (category)
- Product
- Qty Sold
- Turnover
- OrderList (supplier)

**Inventory Data** (`retail_inventory_snapshot_*.csv`):
- Product
- Branch Name
- Dept Fullname
- Branch Stock Level

### Output Features

All features are stored as JSON with the following structure:
- Daily totals (revenue, units, transactions)
- By category (revenue, units, growth rates)
- By location (revenue, traffic, performance vs network)
- By supplier (revenue %, product count)
- Anomalies (z-scores, classifications, multidimensional flags)
- Historical context (7d/30d averages, YoY comparisons)

## Performance Considerations

- **Daily aggregation**: ~5-10 minutes for full day's data
- **Baseline calculation**: ~2-3 minutes for 30-day window
- **Feature caching**: JSON files are fast to read (<100ms)
- **Memory usage**: ~500MB for full dataset in memory

### Optimization Tips

1. Use caching - don't recalculate existing features
2. Run daily batch at night (2-6am) when no sales activity
3. Delete old cache files (>90 days) periodically
4. Use date range filtering when loading sales data

## Troubleshooting

### "No data for date"
- Check if sales data covers that date
- Verify date format (YYYY-MM-DD)
- Ensure Sale Date column is properly formatted

### "Missing baselines"
- Run baseline calculation first
- Check if baselines.json exists in cache directory
- Verify you have at least 30 days of data

### "Anomalies not detected"
- Ensure baselines are calculated correctly
- Check if window_days is appropriate (default: 30)
- Verify anomaly thresholds (z > 2 for significant)

## Example Workflow

```python
from datetime import date, timedelta
from alert_features import *

# 1. Load data
sales_df = pd.read_csv("data/input/Retail/retail_sales_data_*.csv")
inventory_df = pd.read_csv("data/input/Retail/retail_inventory_snapshot_*.csv")

# 2. Initialize components
aggregator = DailyAggregator(sales_df, inventory_df)
calculator = AlertFeatureCalculator(sales_df, inventory_df)
detector = AnomalyDetector()
cache = FeatureCache()

# 3. Build features for yesterday
yesterday = date.today() - timedelta(days=1)

# 3a. Calculate baselines
baselines = detector.calculate_baselines(sales_df, yesterday, window_days=30)
cache.save_baselines(baselines)

# 3b. Aggregate daily features
features = aggregator.aggregate_day(yesterday)

# 3c. Detect anomalies
anomalies = detector.detect_daily_anomalies(features, baselines)
features['anomalies'] = anomalies

# 3d. Save to cache
cache.save_daily_features(features, yesterday)

# 4. Calculate alert-specific features
health_features = calculator.get_health_emergency_features("OTC : Cold & Flu", yesterday)
event_features = calculator.get_major_event_features("Baggot St", yesterday)
supply_features = calculator.get_supply_disruption_features(yesterday)

# 5. Use features in alert decision
if health_features['inventory_health']['alert_needed']:
    print("⚠️  ALERT: Low stock for health emergency!")
```

## Next Steps

1. **Run initial build**: Build features for past 90 days
2. **Set up daily cron job**: Run build script every morning at 5am
3. **Integrate with alert system**: Load features in Context Matcher
4. **Monitor cache size**: Set up periodic cleanup (>90 days)
5. **Export for analysis**: Generate CSV reports weekly

## Support

For questions or issues, see the main documentation in `NEWS_ALERTS_REFOCUSED.md`.
