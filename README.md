# 🚀 Intelligent Business Alerts System

An AI-powered alert system that monitors news, detects relevant events, and generates actionable business intelligence with data-driven insights.

## ✨ Features

### 🎯 **Interactive Demo Dashboard** (NEW!)
- **Web interface** for running the alert pipeline
- **Date picker** with real data dates
- **Real-time progress** tracking with animated progress bar
- **One-click execution** - perfect for demos and presentations
- **Beautiful visualizations** with color-coded severity levels

### 🌅 **Morning Alerts Dashboard**
- **Automated daily briefings** at 8 AM
- **Beautiful animated interface** with smooth transitions
- **Statistics overview** - total, critical, high, moderate alerts
- **Auto-refresh mode** for live monitoring
- **Mobile-friendly** responsive design

### 🤖 **Two-Agent AI Architecture**
- **Agent 1: Event Detector** - Analyzes news and identifies relevant events
- **Agent 2: Context Matcher** - Matches events to business context and generates alerts
- **5 Event Types**: Health emergencies, major events, weather extremes, supply disruptions, viral trends

### 📊 **Data-Driven Intelligence**
- **Real inventory analysis** - Days of supply calculations
- **Sales patterns** - Historical baselines and anomaly detection
- **Geographic precision** - Haversine distance calculations for multi-location impact
- **Supplier criticality** - Revenue dependency analysis
- **Viral trend detection** - Stock availability vs. demand spikes

### 📈 **Historical Analysis**
- **Trend detection** across time periods
- **Pattern recognition** by type, severity, location
- **Automated insights** generation
- **Visual bar charts** with ASCII art
- **Export capabilities** to JSON

## 🚀 Quick Start

### 1. Interactive Demo (Recommended)

Perfect for demos and presentations:

```bash
./launch_demo.sh
```

Then open http://localhost:5000 and:
1. Select a date from the dropdown
2. Click "Run Pipeline"
3. Watch real-time progress
4. View beautiful animated results

See [DEMO_GUIDE.md](DEMO_GUIDE.md) for full details.

### 2. Morning Dashboard

Set up automated daily alerts:

```bash
# Schedule for 8 AM daily
./schedule_morning_alerts.sh install

# Test it now
./schedule_morning_alerts.sh test
```

See [MORNING_DASHBOARD_GUIDE.md](MORNING_DASHBOARD_GUIDE.md) for full details.

### 3. Command Line

Run the full pipeline manually:

```bash
# Demo mode (fast, no API keys)
python run_full_pipeline.py --demo

# With real news (requires API keys)
python run_full_pipeline.py --date 2025-11-15 --use-real-data
```

See [PIPELINE_USAGE.md](PIPELINE_USAGE.md) for full details.

## 📦 Installation

### Prerequisites

- Python 3.8+
- pip

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables (Optional)

For real news fetching:

```bash
export ANTHROPIC_API_KEY="your-key-here"
export NEWS_API_KEY="your-key-here"  # Optional
```

## 📖 Documentation

- **[DEMO_GUIDE.md](DEMO_GUIDE.md)** - Interactive web demo dashboard
- **[MORNING_DASHBOARD_GUIDE.md](MORNING_DASHBOARD_GUIDE.md)** - Scheduled daily alerts
- **[PIPELINE_USAGE.md](PIPELINE_USAGE.md)** - Command-line pipeline details
- **[CONTEXT_MATCHER_GUIDE.md](CONTEXT_MATCHER_GUIDE.md)** - Alert matching logic

## 🎯 Use Cases

### Demo & Presentations

Use the interactive dashboard to wow your audience:

```bash
./launch_demo.sh
```

Select any date, click run, and show the full pipeline executing in real-time with beautiful visualizations.

### Daily Operations

Get automated morning briefings:

```bash
./schedule_morning_alerts.sh install
```

Every morning at 8 AM, you'll get a beautiful dashboard with overnight alerts.

### Historical Analysis

Analyze trends and patterns:

```bash
python analyze_alerts.py --days 30
```

Understand which alert types are most common, busiest locations, confidence trends.

### Real-Time Monitoring

Watch for alerts as they happen:

```bash
python morning_dashboard.py --watch --auto-open
```

Dashboard auto-refreshes every 5 minutes.

## 🏗️ Architecture

### Pipeline Flow

```
1. News Fetching          2. Event Detection           3. Context Matching          4. Alert Generation
   (NewsAPI)     ───────►    (Claude LLM)    ───────►   (Business Rules   ───────►  (Actionable Alerts)
                                                         + Real Data)
```

### File Structure

```
iterate-hackathon/
├── demo_server.py              # Interactive demo backend
├── demo_dashboard.html         # Interactive demo frontend
├── launch_demo.sh              # Demo launcher
├── morning_dashboard.py        # Daily dashboard generator
├── schedule_morning_alerts.sh  # Cron scheduler
├── run_full_pipeline.py        # Pipeline orchestrator
├── run_news_alerts.py          # News fetching & event detection
├── run_context_matcher.py      # Context matching & alert generation
├── analyze_alerts.py           # Historical analysis
├── test_data_integration.py    # Testing & demo events
├── news_alerts/
│   ├── models.py               # Data models (Pydantic)
│   ├── news_fetcher.py         # News API integration
│   ├── event_detector.py       # LLM event detection
│   ├── context_matcher.py      # Business logic + data
│   └── storage.py              # JSON storage
├── alert_features/             # Data engineering
│   ├── calculator.py           # Feature calculation
│   ├── aggregator.py           # Daily aggregations
│   └── detector.py             # Anomaly detection
└── data/
    ├── alerts/                 # Generated alerts (JSON)
    ├── events/                 # Detected events (JSON)
    ├── dashboard/              # HTML dashboards
    └── input/Retail/           # Sales & inventory CSVs
```

## 🎨 Screenshots

### Interactive Demo Dashboard
- Date picker with available dates
- Run Pipeline button with loading state
- Real-time progress bar
- Animated alert cards
- Color-coded severity (Red/Orange/Blue)

### Morning Alerts Dashboard
- Gradient header with beautiful typography
- 6 statistics cards
- Alert cards with event icons
- Confidence progress bars
- Smooth fade/slide animations

## 🔧 Advanced Usage

### Custom Pipeline

```python
from news_alerts.context_matcher import ContextMatcher
from news_alerts.storage import EventStorage

# Initialize with real data
matcher = ContextMatcher(use_real_data=True, enhance_with_llm=True)

# Load events
storage = EventStorage()
events = storage.load_events(target_date="2025-11-15")

# Generate alerts
alerts = matcher.evaluate_events(events)

# Access alert data
for alert in alerts:
    print(f"{alert.severity}: {alert.title}")
    print(f"Confidence: {alert.decision.confidence:.0%}")
```

### Custom Dashboard

```python
from morning_dashboard import MorningDashboard

dashboard = MorningDashboard()
output_file, alert_count = dashboard.generate_and_save(
    output_file=Path("custom_dashboard.html"),
    days=7,
    auto_refresh=True
)
```

### Custom Analysis

```python
from analyze_alerts import analyze_trends

alerts = load_alerts(days=30)
trends = analyze_trends(alerts)

print(f"Most common type: {trends['most_common_type']}")
print(f"Critical rate: {trends['critical_percentage']:.1f}%")
```

## 🧪 Testing

### Run Demo Events

```bash
python test_data_integration.py
```

Creates 5 mock events (health, event, weather, supply, trend) and tests both heuristic and data-driven modes.

### Run Full Pipeline (Demo)

```bash
python run_full_pipeline.py --demo
```

End-to-end test with mock data, no API keys required.

### Run Full Pipeline (Real)

```bash
export ANTHROPIC_API_KEY="your-key"
python run_full_pipeline.py --date 2025-11-15 --use-real-data
```

Full pipeline with real news and data.

## 📊 Data Requirements

### Optional: Sales & Inventory Data

For data-driven mode, place CSV files in `data/input/Retail/`:

- **retail_sales_data_*.csv** - Transaction history
  - Columns: Transaction_Date, Product_Category, Store, Quantity, Revenue
- **retail_inventory_data_*.csv** - Current inventory
  - Columns: Product_Category, Store, Stock_Level

Without these files, the system gracefully falls back to heuristic mode.

## 🎯 Event Types

### 1. Health Emergency (🏥)
- **Triggers**: Outbreaks, disease warnings
- **Data Check**: Inventory levels for medical supplies
- **Action**: Calculate days of supply at elevated demand

### 2. Major Event (🎉)
- **Triggers**: Concerts, sports, festivals
- **Data Check**: Store proximity using Haversine formula
- **Action**: Stock convenience items at nearby locations

### 3. Weather Extreme (⛈️)
- **Triggers**: Heatwaves, storms, cold snaps
- **Data Check**: Seasonal patterns for weather-sensitive products
- **Action**: Ensure adequate stock of relevant categories

### 4. Supply Disruption (📦)
- **Triggers**: Port delays, supplier issues
- **Data Check**: Supplier criticality and dependency
- **Action**: Contact suppliers, find alternatives

### 5. Viral Trend (📱)
- **Triggers**: Social media trends, influencer promotions
- **Data Check**: Product stock vs. potential viral demand
- **Action**: Capitalize on opportunity or prevent stockouts

## 🌟 Key Features Explained

### Multi-Location Intelligence

Uses Haversine formula for accurate distance calculations:

```python
distance = _calculate_distance(
    store_lat, store_lon,
    event_lat, event_lon
)
# Returns distance in kilometers
```

Alerts show exact distances like:
- "Talbot St: 1.62km from event"
- "Ballsbridge: 1.77km from event"

### Confidence Scoring

- **90-100%**: Very High (data-backed)
- **70-89%**: High (strong indicators)
- **50-69%**: Moderate (some uncertainty)
- **<50%**: Low (informational)

### Progressive Enhancement

1. **Heuristics** (always available): Rule-based matching
2. **+ Real Data** (optional): Inventory/sales analysis
3. **+ LLM Enhancement** (optional): Comprehensive business analysis

## 📝 License

[Your license here]

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📧 Support

For questions or issues, please open a GitHub issue or contact [your-email@example.com].

---

**🎉 Ready to get started?**

```bash
# Quick demo
./launch_demo.sh

# Or schedule daily alerts
./schedule_morning_alerts.sh install
```

**Built with ❤️ using Claude AI and modern Python**
