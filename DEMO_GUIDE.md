# 🎯 Interactive Demo Dashboard Guide

Run a beautiful, interactive web demo where you can trigger alerts for any date with a single click!

## ✨ What Is This?

The Interactive Demo Dashboard is a web-based interface that lets you:
- **Select any date** from a dropdown menu (populated from your data)
- **Click a button** to run the full alert pipeline for that date
- **Watch in real-time** as the pipeline executes (with progress bar)
- **View results** immediately in a beautiful animated dashboard

Perfect for demos, presentations, and testing!

## 🚀 Quick Start

### One-Command Launch

```bash
./launch_demo.sh
```

Then open your browser to: **http://localhost:5000**

That's it! 🎉

### What Happens

1. **Server starts** on port 5000
2. **Dashboard opens** in your browser
3. **Dates populate** from your data (or last 30 days if no data)
4. **Ready to demo!**

## 📖 How to Use

### Step 1: Select Date
Click the "Select Date" dropdown and choose any date from the list.

### Step 2: Choose Options
- ✅ **Demo Mode** (checked): Fast execution, no API keys needed
- ⬜ **Use Real Data** (unchecked): Enable if you have sales/inventory CSV files

### Step 3: Run Pipeline
Click the **"🚀 Run Pipeline"** button.

Watch as:
1. Progress bar fills up (0% → 100%)
2. Status messages update in real-time
3. Each pipeline step executes:
   - Building alert features (if using real data)
   - Fetching news / Creating demo events
   - Matching context
   - Generating dashboard

### Step 4: View Results
Once complete, scroll down to see:
- **Statistics cards** - Total alerts, severity breakdown, confidence
- **Alert cards** - Full alert details with animations
- **Color coding** - Red (Critical), Orange (High), Blue (Moderate)

### Step 5: Repeat!
Select a different date and run again. The dashboard updates instantly.

## 🎨 Features

### Interactive Controls
- **Date Picker**: Dropdown with 30-60 available dates
- **Demo Mode Toggle**: Switch between demo and real API calls
- **Real Data Toggle**: Enable data-driven decisions
- **Run Button**: Triggers pipeline with loading state

### Real-Time Progress
- **Progress Bar**: Visual percentage (0-100%)
- **Status Messages**: Step-by-step updates
  - "Initializing..."
  - "Building alert features..."
  - "Fetching news and detecting events..."
  - "Matching context and generating alerts..."
  - "Generating dashboard..."
  - "Complete!"
- **Error Handling**: Shows errors if pipeline fails

### Beautiful Dashboard
- **Statistics Grid**: 6 key metrics with hover effects
- **Alert Cards**: Animated entrance, color-coded severity
- **Confidence Bars**: Animated fill from 0% to actual value
- **Responsive**: Works on desktop, tablet, mobile
- **Dark Theme**: Professional gradient design

### Smooth Animations
- Cards fade in and slide from left
- Statistics pop up from bottom
- Progress bar fills smoothly
- Confidence bars animate on load
- Hover effects on all interactive elements

## 🎯 Use Cases

### 1. Demo for Stakeholders

```bash
./launch_demo.sh
```

Show the live dashboard, select a recent date, click run, and demonstrate the full pipeline in action. Perfect for presentations!

### 2. Testing Different Dates

Want to see how alerts change over time? Select different dates and compare results:
- Pick dates during known events (concerts, weather events)
- Compare weekdays vs. weekends
- Test holiday periods

### 3. Training New Team Members

Let team members interact with the system hands-on:
- Select dates
- Run pipelines
- Review generated alerts
- Understand the decision-making process

### 4. Development Testing

Quickly test pipeline changes:
- Make code modifications
- Select test date
- Run pipeline
- Verify results immediately

## ⚙️ Configuration

### Server Settings

Edit `demo_server.py` to customize:

```python
app.run(host='0.0.0.0', port=5000, debug=False)
```

- **host**: '0.0.0.0' allows external access, '127.0.0.1' for localhost only
- **port**: Change to 8080, 3000, or any available port
- **debug**: Set to True for development (auto-reload on changes)

### Date Range

The dashboard shows:
- **Real data**: Dates from your sales CSV files
- **No data**: Last 30 days from today
- **Limit**: Maximum 60 dates in dropdown

### Pipeline Options

**Demo Mode** (default):
- Creates 5 mock events (health, event, weather, supply, trend)
- Fast execution (~5 seconds)
- No API keys required
- No data files required

**Real Mode**:
- Fetches actual news from NewsAPI
- Requires ANTHROPIC_API_KEY for LLM
- Takes 30-60 seconds
- Generates 10-20 real events

**Real Data Mode**:
- Uses actual sales/inventory CSVs
- Data-driven decisions (higher confidence)
- Requires files in `data/input/Retail/`

## 🔧 Technical Details

### Architecture

```
┌─────────────────┐
│   Browser       │
│  (Dashboard)    │
└────────┬────────┘
         │ HTTP
         ▼
┌─────────────────┐
│  Flask Server   │
│  (demo_server)  │
└────────┬────────┘
         │ subprocess
         ▼
┌─────────────────┐
│  Python Scripts │
│  (pipeline)     │
└─────────────────┘
```

### API Endpoints

**GET /api/dates**
- Returns list of available dates
- Example: `["2025-11-15", "2025-11-14", ...]`

**POST /api/run**
- Triggers pipeline execution
- Body: `{"date": "2025-11-15", "demo_mode": true, "use_real_data": false}`
- Returns: `{"status": "started", "date": "2025-11-15"}`

**GET /api/status**
- Polls pipeline progress
- Returns: `{"running": true, "progress": 60, "step": "Matching context...", "error": null}`

**GET /api/alerts**
- Returns current alerts and statistics
- Returns: `{"alerts": [...], "stats": {...}}`

### Files

- **`demo_server.py`**: Flask backend server (317 lines)
- **`demo_dashboard.html`**: Interactive frontend (687 lines)
- **`launch_demo.sh`**: Launch script with dependency checks (68 lines)

## 🐛 Troubleshooting

### Server Won't Start

**Problem**: `Address already in use` error

**Solution**: Another process is using port 5000
```bash
# Find and kill process on port 5000
lsof -ti:5000 | xargs kill -9

# Or change port in demo_server.py:
app.run(host='0.0.0.0', port=8080)
```

### No Dates in Dropdown

**Problem**: Dropdown shows "Loading dates..." forever

**Solution**:
1. Check browser console for errors (F12)
2. Verify server is running
3. Check server logs for errors

### Pipeline Fails

**Problem**: Error shown in red box

**Solutions**:
- **Demo mode**: Ensure `test_data_integration.py` exists and runs
- **Real mode**: Check ANTHROPIC_API_KEY environment variable
- **Real data**: Verify CSV files in `data/input/Retail/`

### Dashboard Not Updating

**Problem**: Clicked run but dashboard doesn't refresh

**Solution**:
1. Wait for "Complete!" message
2. Check browser console for errors
3. Manually refresh page if needed
4. Verify alerts created in `data/alerts/`

### Can't Access from Another Device

**Problem**: Want to demo on another computer/phone

**Solution**:
1. Ensure server uses `host='0.0.0.0'` (not '127.0.0.1')
2. Find your IP: `hostname -I` or `ifconfig`
3. Open `http://<your-ip>:5000` on other device
4. Check firewall allows port 5000

## 💡 Tips & Tricks

### Faster Demos

Keep demo mode enabled for instant results:
```
✅ Demo Mode
⬜ Use Real Data
```

This runs in ~5 seconds with consistent results.

### More Realistic Demos

Disable demo mode for real news:
```
⬜ Demo Mode
✅ Use Real Data
```

Requires API keys but shows actual news-based alerts.

### Show Data-Driven Intelligence

Enable real data to demonstrate higher confidence:
```
✅ Demo Mode
✅ Use Real Data
```

Shows how real sales/inventory data improves decisions.

### Pre-Generate Alerts

Before a presentation, pre-generate alerts for interesting dates:
```bash
python run_full_pipeline.py --date 2025-11-15 --demo
python run_full_pipeline.py --date 2025-11-16 --demo
python run_full_pipeline.py --date 2025-11-17 --demo
```

Then demo is instant - just select date and click!

### Multiple Dates Comparison

Open dashboard in multiple browser tabs, each with different dates, to compare side-by-side.

### Custom Styling

Edit colors in `demo_dashboard.html`:
```css
:root {
    --accent: #3b82f6;      /* Change accent color */
    --critical: #ef4444;    /* Change critical color */
    --bg-primary: #0f172a;  /* Change background */
}
```

## 📚 Related Documentation

- **Morning Dashboard**: `MORNING_DASHBOARD_GUIDE.md` - Scheduled daily dashboard
- **Pipeline Usage**: `PIPELINE_USAGE.md` - Command-line pipeline details
- **Context Matcher**: `CONTEXT_MATCHER_GUIDE.md` - Alert matching logic
- **Historical Analysis**: See `analyze_alerts.py` for trend analysis

## 🎬 Example Demo Script

Here's a suggested script for presenting:

> "Let me show you our intelligent alert system in action.
>
> [Open http://localhost:5000]
>
> This is our interactive dashboard. I can select any date from our historical data...
>
> [Select date with known event, e.g., concert date]
>
> Now I'll run the alert pipeline by clicking this button.
>
> [Click Run Pipeline]
>
> Watch as it processes in real-time - it's analyzing news, detecting events, matching business context, and generating actionable alerts.
>
> [Wait for progress bar to complete - ~5 seconds]
>
> And there we have it! The system detected [X] alerts, including [Y] critical ones. Let's look at this one...
>
> [Scroll to alert card]
>
> Notice how it provides specific recommendations, affected product categories, and impacted store locations. The decision confidence is [Z]% because we're using real sales and inventory data.
>
> Let's try a different date...
>
> [Select another date and repeat]"

---

**🎉 Ready to demo? Run `./launch_demo.sh` and impress your audience!**
