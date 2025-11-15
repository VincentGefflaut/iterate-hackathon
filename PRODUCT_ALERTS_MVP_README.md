# Product Alerts MVP - Integration Guide

## Overview

This MVP integrates the `top.csv` data (top 3 products by location) with the existing news alerts pipeline to create a product-focused event detection and alerting system.

## What Was Built

### 1. **Top Products Data Loader** (`news_alerts/top_products_loader.py`)
- Parses `top.csv` to extract locations and their top 3 products
- Provides access to:
  - All locations with their top products
  - Top N locations by sales volume
  - Unique products across all locations
  - Locations filtered by country

### 2. **Product-Aware News Fetcher** (`news_alerts/product_news_fetcher.py`)
- Extends the base `NewsFetcher` with product-specific queries
- Fetches news based on location + product combinations
- Key features:
  - Targeted queries combining location and product (e.g., "Dublin Ireland vitamins shortage")
  - Health and product news aggregation
  - Smart query building based on product type
  - Deduplication of articles

### 3. **Product Event Detector** (`news_alerts/product_event_detector.py`)
- Extends `EventDetectorAgent` to focus on product-related events
- Uses Claude AI to detect 5 types of product-impacting events:
  1. **Health Trends**: Outbreaks/conditions that increase product demand
  2. **Supply Disruption**: Shortages, recalls, supply chain issues
  3. **Regulatory Change**: New regulations affecting products
  4. **Viral Trend**: Social media trends driving demand
  5. **Competitor Action**: Competitor promotions/actions
- Extracts structured data including:
  - Affected products
  - Affected geographic areas
  - Severity, confidence, urgency
  - Key facts and potential business impact

### 4. **MVP Pipeline Script** (`run_product_alerts_mvp.py`)
- Complete end-to-end pipeline for today's date
- Features:
  - Loads top.csv data
  - Fetches product-related news for top N locations
  - Detects product events using Claude AI
  - Generates actionable alerts
  - Saves alerts to JSON files

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        top.csv                              │
│  (Locations + Top 3 Products by Sales Volume)              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              TopProductsLoader                              │
│  • Parse CSV                                                │
│  • Extract locations & products                            │
│  • Rank by sales volume                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│           ProductNewsFetcher                                │
│  • Build queries: Location + Product                       │
│  • Fetch from NewsAPI / Google News                        │
│  • Deduplicate articles                                    │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         ProductEventDetector (Claude AI)                    │
│  • Analyze articles for product events                     │
│  • Extract structured data                                 │
│  • Identify affected products & areas                      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Alert Generation                           │
│  • Filter by severity threshold                            │
│  • Generate recommended actions                            │
│  • Save to data/alerts/                                    │
└─────────────────────────────────────────────────────────────┘
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Required for event detection
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional - enhances news fetching (100 free requests/day)
NEWS_API_KEY=your-newsapi-key-here
```

Get API keys:
- **Anthropic**: https://console.anthropic.com/
- **NewsAPI**: https://newsapi.org/register (optional, free tier available)

### 3. Verify Setup

```bash
# Test components
python test_mvp_components.py
```

## Usage

### Demo Mode (Recommended First)

Test with sample product-related articles:

```bash
python run_product_alerts_mvp.py --demo
```

This will:
- Use 3 pre-written sample articles (vitamin shortage, serum trend, cleanser recall)
- Detect events using Claude AI
- Generate alerts
- **No NewsAPI key required** (uses demo data)
- **Requires ANTHROPIC_API_KEY**

### Production Mode

Run for today's date with real news:

```bash
# Default: Top 5 locations, max 50 articles, medium+ severity
python run_product_alerts_mvp.py

# Custom settings
python run_product_alerts_mvp.py --top-n 10 --max-articles 100 --severity high

# Monitor specific number of locations
python run_product_alerts_mvp.py --top-n 3

# Only high/critical alerts
python run_product_alerts_mvp.py --severity high
```

**Production mode requires:**
- `ANTHROPIC_API_KEY` (required)
- `NEWS_API_KEY` (recommended) or fallback to free RSS feeds

### Command-Line Options

```bash
--top-n N          # Monitor top N locations by sales (default: 5)
--max-articles N   # Max articles to process (default: 50, controls API costs)
--severity LEVEL   # Minimum severity: low/medium/high/critical (default: medium)
--demo             # Run demo mode with sample data
```

## Output

### Console Output

```
================================================================================
  PRODUCT ALERTS MVP - INTEGRATED PIPELINE
================================================================================

📅 Date: 2025-11-15
📍 Monitoring: Top 5 locations by sales volume
📰 Max articles: 50
⚠️  Alert threshold: medium

--------------------------------------------------------------------------------
  STEP 1: Load Top Products Data
--------------------------------------------------------------------------------
✓ Loaded data for 21 locations
✓ Tracking 3 unique products: Cleanser, Serum, Vitamins & Supplements

Top locations to monitor:
  1. Dublin, Ireland (363,922 sales)
     Top products: Vitamins & Supplements, Cleanser, Serum
  2. Cork, Ireland (168,496 sales)
     Top products: Vitamins & Supplements, Cleanser, Serum
  ...

--------------------------------------------------------------------------------
  STEP 3: Detect Product-Related Events
--------------------------------------------------------------------------------

  [1/50] Vitamin D Shortage Hits Irish Pharmacies...
    ✓ EVENT: supply_disruption
      Products: Vitamins & Supplements
      Severity: high | Confidence: high

  [2/50] Viral TikTok Trend Drives Serum Sales...
    ✓ EVENT: viral_trend
      Products: Serum
      Severity: medium | Confidence: high

...

================================================================================
  PRODUCT ALERTS
================================================================================

🚨 ALERT #1
   ID: ALERT_20251115_140523_1
   Type: supply_disruption | Severity: high | Urgency: immediate
   Title: Vitamin D Shortage Hits Irish Pharmacies
   Affected Products: Vitamins & Supplements
   Affected Areas: Dublin, Cork, Galway

   Description:
   Pharmacies across Ireland report shortages of Vitamin D supplements...

   Key Facts:
     • Multiple chains affected
     • Winter demand surge
     • Suppliers struggling

   Potential Impact:
   Supply shortage may lead to stockouts. Customer demand unmet.

   Recommended Action:
   URGENT: Check inventory levels. Contact suppliers to confirm stock.

   Source: https://example.com/vitamin-shortage
```

### JSON Output

Alerts are saved to `data/alerts/product_alerts_YYYY-MM-DD.json`:

```json
{
  "date": "2025-11-15",
  "generated_at": "2025-11-15T14:05:23",
  "total_alerts": 2,
  "severity_threshold": "medium",
  "tracked_locations": ["Dublin, Ireland", "Cork, Ireland", ...],
  "tracked_products": ["Vitamins & Supplements", "Cleanser", "Serum"],
  "alerts": [
    {
      "alert_id": "ALERT_20251115_140523_1",
      "event_type": "supply_disruption",
      "title": "Vitamin D Shortage Hits Irish Pharmacies",
      "severity": "high",
      "urgency": "immediate",
      "affected_products": ["Vitamins & Supplements"],
      "affected_areas": ["Dublin", "Cork", "Galway"],
      "location": "Ireland",
      "event_date": "2025-11-15",
      "description": "...",
      "key_facts": ["...", "..."],
      "potential_relevance": "...",
      "source_url": "...",
      "detected_at": "2025-11-15T14:05:23",
      "recommended_action": "URGENT: Check inventory levels..."
    }
  ]
}
```

## Product Coverage

From `top.csv`, the system tracks:

1. **Vitamins & Supplements** (top product in all locations)
2. **Cleanser** (top 2-3 in most locations)
3. **Serum** (top 2-3 in most locations)

## Location Coverage

Top locations by sales volume:
1. Dublin, Ireland (363,922 sales)
2. Cork, Ireland (168,496 sales)
3. Galway, Ireland (109,988 sales)
4. Kildare, Ireland (92,791 sales)
5. Meath, Ireland (73,805 sales)
...and 16 more locations

## Event Types Detected

1. **Health Trends**: Flu outbreak → Vitamins demand ⬆
2. **Supply Disruption**: Vitamin shortage reported
3. **Regulatory Change**: OTC reclassification
4. **Viral Trend**: TikTok serum trend → Sales surge
5. **Competitor Action**: Boots mega promotion

## API Costs

### Anthropic Claude (Required)
- **Model**: Claude Sonnet 4.5
- **Cost**: ~$0.003 per article analyzed
- **Default**: 50 articles/day = ~$0.15/day = ~$4.50/month
- **Control**: Use `--max-articles` to limit

### NewsAPI (Optional)
- **Free tier**: 100 requests/day
- **Fallback**: Free RSS feeds (Google News, Met Éireann)

## Integration with Existing Pipeline

This MVP integrates seamlessly with the existing news alerts system:

- ✅ Uses existing `EventStorage` for saving events
- ✅ Compatible with existing `ContextMatcher` for business context
- ✅ Follows same architecture patterns
- ✅ Can be combined with `run_full_pipeline.py`

## Testing

### Test Components
```bash
python test_mvp_components.py
```

### Test with Demo Data
```bash
python run_product_alerts_mvp.py --demo
```

### Test with Real News (requires API keys)
```bash
python run_product_alerts_mvp.py --top-n 3 --max-articles 20
```

## Files Created

```
iterate-hackathon/
├── top.csv                              # Input data (already exists)
├── run_product_alerts_mvp.py           # Main MVP script (NEW)
├── test_mvp_components.py              # Component tests (NEW)
├── PRODUCT_ALERTS_MVP_README.md        # This file (NEW)
│
└── news_alerts/
    ├── __init__.py                      # Updated with new exports
    ├── top_products_loader.py          # NEW: CSV parser
    ├── product_news_fetcher.py         # NEW: Product-aware fetcher
    └── product_event_detector.py       # NEW: Product event detector
```

## Next Steps

1. **Test the MVP**:
   ```bash
   python run_product_alerts_mvp.py --demo
   ```

2. **Run for Production** (with API keys set):
   ```bash
   python run_product_alerts_mvp.py --top-n 5 --max-articles 50
   ```

3. **Review Alerts**:
   ```bash
   cat data/alerts/product_alerts_*.json
   ```

4. **Integrate with Context Matcher** (optional):
   - Use detected events with existing `run_context_matcher.py`
   - Match product events to inventory/sales data

5. **Schedule Daily Runs** (optional):
   ```bash
   # Add to crontab for daily execution
   0 9 * * * cd /path/to/project && python run_product_alerts_mvp.py
   ```

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
- Create `.env` file with `ANTHROPIC_API_KEY=your-key`
- Or export: `export ANTHROPIC_API_KEY=your-key`

### "No articles found"
- Set `NEWS_API_KEY` in `.env` for better results
- Google News RSS may be blocked (use NewsAPI instead)
- Try `--demo` mode to test with sample data

### "Module not found" errors
- Run: `pip install -r requirements.txt`

### High API costs
- Reduce `--max-articles` (default: 50)
- Reduce `--top-n` locations (default: 5)
- Use `--demo` mode for testing

## Summary

✅ **Integrated top.csv data** with news alerts pipeline
✅ **Product-focused news fetching** based on locations + products
✅ **AI-powered event detection** using Claude for product-related events
✅ **Actionable alerts** with severity levels and recommendations
✅ **JSON output** for downstream processing
✅ **Demo mode** for testing without API keys
✅ **Cost controls** via command-line options

The MVP is ready to run for today's date and will generate alerts for product-related events affecting your top locations and products!
