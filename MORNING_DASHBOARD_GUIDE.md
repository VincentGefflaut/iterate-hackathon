# 🌅 Morning Alerts Dashboard Guide

Beautiful, animated web dashboard for viewing your daily business alerts.

## ✨ Features

- **Beautiful Design**: Modern dark theme with smooth gradient backgrounds
- **Animated Interface**: Fade-in, slide-in animations for cards and statistics
- **Real-time Statistics**:
  - Total alerts count
  - Critical/High/Moderate severity breakdown
  - Average decision confidence
  - Number of affected locations
- **Color-Coded Alerts**: Visual severity indicators (Red=Critical, Orange=High, Blue=Moderate, Green=Low)
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Auto-Refresh**: Optional automatic updates every 5 minutes
- **Event Type Icons**: Visual icons for each alert type (🏥 Health, 🎉 Events, ⛈️ Weather, 📦 Supply, 📱 Trends)

## 🚀 Quick Start

### Generate Dashboard Now

```bash
# View today's alerts
python morning_dashboard.py --auto-open

# View last 7 days of alerts
python morning_dashboard.py --days 7 --auto-open

# Enable auto-refresh (updates every 5 minutes)
python morning_dashboard.py --watch --auto-open
```

### Schedule for Every Morning

```bash
# Install cron job to run at 8:00 AM daily
./schedule_morning_alerts.sh install

# Test it now
./schedule_morning_alerts.sh test

# Check schedule status
./schedule_morning_alerts.sh status

# Remove scheduled job
./schedule_morning_alerts.sh uninstall
```

## 📋 Usage Examples

### Example 1: Daily Morning Routine

Set up the dashboard to automatically open every morning at 8 AM:

```bash
./schedule_morning_alerts.sh install
```

This will:
- Run the full pipeline every morning
- Generate the dashboard
- Automatically open it in your browser
- Show alerts from the last 24 hours

### Example 2: Custom Time Range

View alerts from the last week:

```bash
python morning_dashboard.py --days 7 --auto-open
```

### Example 3: Live Monitoring

Create a live dashboard that auto-refreshes:

```bash
python morning_dashboard.py --watch --auto-open
```

The dashboard will update every 5 minutes automatically.

### Example 4: Custom Output Location

```bash
python morning_dashboard.py --output ~/Desktop/alerts.html --auto-open
```

## ⚙️ Configuration

### Scheduling Configuration

Edit `schedule_morning_alerts.sh` to customize:

```bash
# Time settings (24-hour format)
HOUR="08"        # 8 AM
MINUTE="00"      # At exactly 00 minutes

# Dashboard settings
DAYS="1"         # Show last 1 day of alerts
AUTO_OPEN="true" # Automatically open in browser
```

Common schedules:
- **Morning briefing**: `HOUR="08"` `MINUTE="00"`
- **Lunch update**: `HOUR="12"` `MINUTE="30"`
- **End of day**: `HOUR="17"` `MINUTE="00"`

### Alert Time Range

Control how many days of alerts to display:

```bash
# Today only
python morning_dashboard.py --days 1

# This week
python morning_dashboard.py --days 7

# This month
python morning_dashboard.py --days 30
```

## 📊 Dashboard Components

### Statistics Cards

The dashboard displays 6 key metrics:

1. **Total Alerts**: Count of all alerts in the time period
2. **Critical Alerts**: Alerts requiring immediate action (red)
3. **High Priority**: Alerts to review today (orange)
4. **Moderate Alerts**: Alerts to monitor (blue)
5. **Average Confidence**: Mean confidence score of all alerts
6. **Affected Locations**: Number of unique store locations impacted

### Alert Cards

Each alert card shows:

- **Title**: Event name with type icon
- **Severity Badge**: Color-coded priority level
- **Metadata**: Time, date, and event type
- **Description**: Brief summary of the alert
- **Affected Categories**: Product categories impacted (up to 5 shown)
- **Store Locations**: Affected stores (up to 3 shown with "+X more")
- **Confidence Bar**: Visual and percentage representation of decision confidence

### Animations

The dashboard features smooth animations:

- **Header**: Fade-in from top
- **Statistics**: Fade-in from bottom with stagger
- **Alert Cards**: Slide-in from left with progressive delay
- **Confidence Bars**: Animate from 0% to actual value on page load
- **Hover Effects**: Cards lift and expand shadow on hover

## 🎨 Visual Design

### Color Scheme

- **Critical**: Red (#ef4444) - Immediate action required
- **High**: Orange (#f97316) - Review today
- **Moderate**: Blue (#3b82f6) - Monitor closely
- **Low**: Green (#10b981) - Informational

### Event Type Icons

- 🏥 **Health Emergency**: Medical/safety events
- 🎉 **Major Event**: Concerts, sports, festivals
- ⛈️ **Weather Extreme**: Heat waves, storms, cold snaps
- 📦 **Supply Disruption**: Shipping, supplier issues
- 📱 **Viral Trend**: Social media trends, product spikes

## 🔧 Advanced Usage

### Integrate with Full Pipeline

Run the complete pipeline and generate dashboard:

```bash
# With real data
python run_full_pipeline.py --date 2025-11-15 --use-real-data
python morning_dashboard.py --auto-open

# Demo mode (no API keys needed)
python run_full_pipeline.py --demo
python morning_dashboard.py --auto-open
```

### Combine with Historical Analysis

Generate insights then view dashboard:

```bash
# Analyze patterns
python analyze_alerts.py --days 30

# View alerts
python morning_dashboard.py --days 30 --auto-open
```

### Automated Email (Advanced)

Combine with email tools to send the dashboard:

```bash
#!/bin/bash
# Generate dashboard
python morning_dashboard.py --days 1 --output /tmp/dashboard.html

# Send via email (requires mail/sendmail configured)
cat /tmp/dashboard.html | mail -s "Morning Alerts Dashboard" \
  -a "Content-Type: text/html" your@email.com
```

## 📁 Output Files

### Dashboard Location

Default: `data/dashboard/morning_alerts.html`

The dashboard is a standalone HTML file that includes:
- All CSS styling embedded
- JavaScript for animations
- No external dependencies
- Can be shared or archived

### Viewing Options

1. **Auto-open in browser** (recommended):
   ```bash
   python morning_dashboard.py --auto-open
   ```

2. **Manual open**:
   - Double-click `data/dashboard/morning_alerts.html`
   - Or drag it into your browser

3. **Direct path**:
   ```
   file:///home/user/iterate-hackathon/data/dashboard/morning_alerts.html
   ```

## 🐛 Troubleshooting

### No Alerts Displayed

**Problem**: Dashboard shows "No alerts in the selected time period"

**Solutions**:
```bash
# Generate demo alerts
python run_full_pipeline.py --demo

# Or run the full pipeline with real data
python run_full_pipeline.py --date $(date +%Y-%m-%d) --use-real-data

# Then regenerate dashboard
python morning_dashboard.py --auto-open
```

### Cron Job Not Running

**Problem**: Dashboard doesn't open automatically in the morning

**Solutions**:
```bash
# Check if cron job is installed
./schedule_morning_alerts.sh status

# Check cron logs
tail -f data/logs/morning_dashboard.log

# Verify cron service is running
sudo systemctl status cron  # On Linux
```

### Browser Doesn't Auto-Open

**Problem**: `--auto-open` flag doesn't work

**Solutions**:
```bash
# Try opening manually
open data/dashboard/morning_alerts.html  # macOS
xdg-open data/dashboard/morning_alerts.html  # Linux

# Or use full path
firefox file:///home/user/iterate-hackathon/data/dashboard/morning_alerts.html
```

### Animations Not Working

**Problem**: Dashboard appears but no animations

**Cause**: JavaScript disabled or old browser

**Solutions**:
- Enable JavaScript in browser settings
- Use a modern browser (Chrome, Firefox, Safari, Edge)
- The dashboard still works without animations, just less pretty!

## 💡 Tips & Best Practices

### Morning Routine

1. **Schedule it**: Use cron to run automatically at 8 AM
2. **Review critical first**: Red cards need immediate attention
3. **Check confidence**: High confidence (90%+) alerts are data-backed
4. **Follow action items**: Each alert includes specific next steps

### Monitoring

1. **Weekly review**: Run `--days 7` every Monday to see weekly trends
2. **Combine with analysis**: Use `analyze_alerts.py` for deeper insights
3. **Archive important dashboards**: Save HTML files for record-keeping
4. **Watch mode**: Use `--watch` for real-time monitoring during events

### Performance

- **Fast generation**: Takes <1 second for 100 alerts
- **Lightweight**: Single HTML file, ~100KB typical size
- **No internet**: Works offline, no external dependencies
- **Mobile friendly**: Responsive design works on phones/tablets

## 🎯 Use Cases

### 1. Daily Executive Briefing

```bash
# Every morning at 8 AM
./schedule_morning_alerts.sh install
```

Start your day with a visual overview of critical business alerts.

### 2. Incident Response Dashboard

```bash
# Live monitoring during crisis
python morning_dashboard.py --watch --auto-open
```

Keep dashboard open for real-time updates every 5 minutes.

### 3. Weekly Business Review

```bash
# Monday morning review
python morning_dashboard.py --days 7 --auto-open
```

Review the past week's alerts to identify patterns.

### 4. Multi-Day Event Monitoring

```bash
# During major event (e.g., festival weekend)
python morning_dashboard.py --days 3 --watch --auto-open
```

Monitor alerts across the event duration with auto-refresh.

## 🌟 What's Next?

Once you're comfortable with the basic dashboard, explore:

1. **Historical Analysis**: Use `analyze_alerts.py` for trend detection
2. **Data-Driven Mode**: Add real sales/inventory data for higher confidence
3. **LLM Enhancements**: Enable comprehensive business analysis
4. **Full Pipeline**: Automate everything from news fetch to dashboard

---

**Need help?** Check the main documentation:
- Pipeline usage: `PIPELINE_USAGE.md`
- Context matching: `CONTEXT_MATCHER_GUIDE.md`
- Alert features: See `alert_features/` package
