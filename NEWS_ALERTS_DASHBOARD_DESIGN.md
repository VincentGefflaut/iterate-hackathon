# AI-Powered News Alerts Dashboard for Retail Sales Impact
## Design Document & Implementation Guide

---

## 🎯 Executive Summary

**Goal**: Build an automated daily alerts system that monitors news and identifies events that could impact retail pharmacy sales.

**Examples of Actionable Alerts**:
- 🦠 "Flu outbreak reported in Dublin - expect 40% spike in cold/flu medication sales"
- 🌡️ "Heatwave forecasted next week - stock up on sunscreen, hydration products"
- 💊 "New vitamin study published - consumer interest in Vitamin D will surge"
- 🏪 "Competitor opening new location in Churchtown - prepare defensive promotions"
- 📺 "Celebrity endorsement of skincare brand - expect demand increase"

---

## 🏗️ System Architecture

### **Multi-Agent Architecture (Recommended)**

```
┌─────────────────────────────────────────────────────────────────┐
│                     ORCHESTRATOR AGENT                          │
│  (Daily scheduler, coordinates all agents, generates report)   │
└───────────────┬─────────────────────────────────────────────────┘
                │
        ┌───────┴────────┬──────────────┬──────────────┐
        │                │              │              │
        ▼                ▼              ▼              ▼
┌───────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│ NEWS SCOUT    │ │ RELEVANCE    │ │ IMPACT       │ │ ACTION       │
│ AGENT         │ │ FILTER AGENT │ │ ANALYZER     │ │ RECOMMENDER  │
│               │ │              │ │ AGENT        │ │ AGENT        │
└───────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
   Fetches news    Filters noise    Predicts impact  Suggests actions
   from multiple    Scores           Quantifies       Generates
   sources          relevance        sales change     recommendations
```

### **Why Multi-Agent vs Single Agent?**

**Multi-Agent Approach** (Recommended):
✅ **Specialization**: Each agent masters one task (news fetching, filtering, analysis, recommendations)
✅ **Parallel Processing**: Run agents concurrently for speed
✅ **Easier Debugging**: Isolate which agent is underperforming
✅ **Incremental Improvement**: Upgrade one agent without touching others
✅ **Auditability**: See each step's output (transparency)

**Single Agent Approach**:
❌ Tries to do everything → mediocre at all tasks
❌ Hard to debug when something goes wrong
❌ Slow (sequential processing)
❌ All-or-nothing upgrades

**Example Comparison**:
```python
# ❌ Single Agent (monolithic)
agent.run("Find news and analyze impact and recommend actions")
# What if it finds news but misses impact? Hard to debug.

# ✅ Multi-Agent (specialized)
news = news_scout.fetch()           # Returns structured news objects
relevant = relevance_filter.score(news)  # Returns scored, filtered list
impacts = impact_analyzer.predict(relevant)  # Returns quantified predictions
actions = action_recommender.suggest(impacts)  # Returns action items

# Each step is visible, debuggable, improvable
```

---

## 📰 Agent 1: News Scout Agent

**Purpose**: Fetch relevant news from multiple sources

### **Data Sources** (Prioritized):

1. **News APIs** (Free tiers available):
   - **NewsAPI.org** (Free: 100 requests/day, 1 month history)
     - Good for general news
     - Easy to filter by country (Ireland), category (health, business)

   - **GDELT** (Free, massive dataset)
     - Real-time global news monitoring
     - Sentiment analysis included
     - Can be overwhelming (need strong filtering)

   - **Google News RSS** (Free, simple)
     - No API key needed
     - Can filter by location/topic
     - Limited to RSS parsing

2. **Specialized Sources**:
   - **Twitter/X API** (trends, real-time mentions)
   - **Reddit API** (r/ireland, r/Dublin for local buzz)
   - **Government Sites** (health.gov.ie for official alerts)
   - **Weather APIs** (Met Éireann, OpenWeather)

3. **Retail-Specific**:
   - **Google Trends API** (detect surge in product searches)
   - **Competitor websites** (scrape press releases)
   - **Industry newsletters** (Retail Ireland, PharmaTimes)

### **Implementation**:

```python
from typing import List, Dict
from datetime import datetime, timedelta
import requests

class NewsScoutAgent:
    """
    Fetches news from multiple sources daily
    """

    def __init__(self, config: Dict):
        self.newsapi_key = config.get('newsapi_key')
        self.gdelt_enabled = config.get('gdelt_enabled', False)
        self.search_keywords = config.get('keywords', [
            'flu', 'covid', 'health', 'pharmacy',
            'vitamin', 'skincare', 'retail', 'Dublin',
            'Ireland health', 'medication', 'supplement'
        ])

    def fetch_daily_news(self) -> List[Dict]:
        """
        Fetch news from last 24 hours
        Returns list of news articles
        """
        all_news = []

        # Source 1: NewsAPI
        all_news.extend(self._fetch_newsapi())

        # Source 2: Google News RSS
        all_news.extend(self._fetch_google_news_rss())

        # Source 3: Weather forecast (affects sales!)
        all_news.extend(self._fetch_weather_forecast())

        # Source 4: Google Trends (detect surges)
        all_news.extend(self._fetch_google_trends())

        # Deduplicate by URL
        unique_news = self._deduplicate(all_news)

        return unique_news

    def _fetch_newsapi(self) -> List[Dict]:
        """Fetch from NewsAPI.org"""
        if not self.newsapi_key:
            return []

        url = "https://newsapi.org/v2/everything"

        # Search for relevant keywords in Irish news
        params = {
            'apiKey': self.newsapi_key,
            'q': ' OR '.join(self.search_keywords),
            'language': 'en',
            'from': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
            'sortBy': 'relevancy',
            'pageSize': 100
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            articles = response.json().get('articles', [])
            return [self._format_article(a, 'NewsAPI') for a in articles]

        return []

    def _fetch_google_news_rss(self) -> List[Dict]:
        """Fetch from Google News RSS (free, no API key)"""
        import feedparser

        articles = []

        # Google News RSS for health news in Ireland
        rss_urls = [
            'https://news.google.com/rss/search?q=health+Ireland&hl=en-IE&gl=IE&ceid=IE:en',
            'https://news.google.com/rss/search?q=pharmacy+Ireland&hl=en-IE&gl=IE&ceid=IE:en',
            'https://news.google.com/rss/search?q=flu+Dublin&hl=en-IE&gl=IE&ceid=IE:en',
        ]

        for rss_url in rss_urls:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:20]:  # Limit per feed
                articles.append({
                    'source': 'Google News RSS',
                    'title': entry.title,
                    'url': entry.link,
                    'published_at': entry.get('published', str(datetime.now())),
                    'description': entry.get('summary', ''),
                    'content': entry.get('summary', '')
                })

        return articles

    def _fetch_weather_forecast(self) -> List[Dict]:
        """
        Fetch weather forecast (impacts sales significantly!)

        Examples:
        - Heatwave → sunscreen, hydration sales up
        - Cold snap → flu meds, vitamin C up
        - Rain → indoor products, comfort items
        """
        # Use OpenWeather API or Met Éireann
        # This is a "news" item because weather IS a sales driver

        url = "http://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': 'Dublin,IE',
            'appid': 'YOUR_OPENWEATHER_KEY',
            'units': 'metric'
        }

        # Parse forecast and create "news" items for extreme weather
        # Example: "Heatwave Alert: Temperatures above 25°C for next 5 days"

        return []  # Implement based on your needs

    def _fetch_google_trends(self) -> List[Dict]:
        """
        Detect surge in search interest for products

        Example: Sudden 200% spike in "Vitamin D" searches
        → Create alert about trend
        """
        from pytrends.request import TrendReq

        # Monitor product categories
        keywords = ['vitamin D', 'face mask', 'hand sanitizer', 'flu medicine']

        # This would detect trends and create "news" items
        # Example: "Search Surge Alert: 'Vitamin D' searches up 150% this week"

        return []  # Implement based on your needs

    def _format_article(self, article: Dict, source: str) -> Dict:
        """Standardize article format across sources"""
        return {
            'source': source,
            'title': article.get('title', ''),
            'url': article.get('url', ''),
            'published_at': article.get('publishedAt', str(datetime.now())),
            'description': article.get('description', ''),
            'content': article.get('content', ''),
            'raw': article  # Keep original for debugging
        }

    def _deduplicate(self, articles: List[Dict]) -> List[Dict]:
        """Remove duplicate articles by URL"""
        seen_urls = set()
        unique = []

        for article in articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique.append(article)

        return unique
```

---

## 🎯 Agent 2: Relevance Filter Agent

**Purpose**: Filter noise, score relevance to retail pharmacy sales

**Challenge**: You'll get 100+ news articles daily, but only 5-10 are actually relevant.

### **Relevance Scoring Criteria**:

1. **Geographic Relevance** (0-10 points)
   - Dublin/Ireland mentioned: +10
   - Europe mentioned: +5
   - Global: +2

2. **Topic Relevance** (0-20 points)
   - Health/pharmacy directly mentioned: +20
   - Consumer behavior: +15
   - Economy/retail: +10
   - Weather (affects sales): +15

3. **Urgency** (0-15 points)
   - Breaking news: +15
   - Published today: +10
   - Published this week: +5

4. **Product Category Match** (0-25 points)
   - Matches your top product categories (vitamins, OTC, skincare)
   - Use your actual sales data to weight categories

5. **Actionability** (0-30 points)
   - Can take action within 7 days: +30
   - Can take action within 30 days: +20
   - Informational only: +5

**Total Relevance Score**: 0-100

**Threshold**: Only pass articles with score ≥60 to next agent

### **Implementation**:

```python
from typing import List, Dict
from pydantic import BaseModel

class ScoredArticle(BaseModel):
    """Structured output for scored articles"""
    article: Dict
    relevance_score: int  # 0-100
    geographic_score: int
    topic_score: int
    urgency_score: int
    category_match_score: int
    actionability_score: int
    reasoning: str
    should_analyze: bool

class RelevanceFilterAgent:
    """
    Filters and scores news articles for relevance
    Uses LLM for intelligent scoring
    """

    def __init__(self, anthropic_client, product_categories: List[str]):
        self.client = anthropic_client
        self.product_categories = product_categories

    def score_articles(self, articles: List[Dict]) -> List[ScoredArticle]:
        """
        Score each article for relevance
        Returns only articles worth analyzing (score ≥ 60)
        """
        scored = []

        for article in articles:
            score = self._score_single_article(article)
            if score.should_analyze:
                scored.append(score)

        # Sort by relevance (highest first)
        scored.sort(key=lambda x: x.relevance_score, reverse=True)

        return scored

    def _score_single_article(self, article: Dict) -> ScoredArticle:
        """Score a single article using Claude"""

        prompt = f"""
You are a retail pharmacy analyst evaluating news relevance.

Article:
Title: {article['title']}
Description: {article['description']}
Content: {article.get('content', 'N/A')[:500]}...
Published: {article['published_at']}

Our Product Categories (for reference):
{', '.join(self.product_categories)}

Score this article on:
1. Geographic Relevance (0-10): Is it relevant to Dublin/Ireland?
2. Topic Relevance (0-20): Does it relate to health, pharmacy, retail, consumer behavior?
3. Urgency (0-15): How time-sensitive is this?
4. Category Match (0-25): Does it relate to our product categories?
5. Actionability (0-30): Can we take action based on this within 30 days?

Provide:
- Individual scores for each dimension
- Total relevance score (sum of all)
- Brief reasoning
- Whether to analyze further (threshold: ≥60)

Think step-by-step about how this news could impact retail pharmacy sales.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            temperature=0.3,  # Lower temp for consistent scoring
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "score_article",
                "description": "Score article relevance",
                "input_schema": ScoredArticle.schema()
            }]
        )

        # Extract structured output
        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            scored = ScoredArticle(**tool_use.input, article=article)
            return scored

        # Fallback: low score if parsing failed
        return ScoredArticle(
            article=article,
            relevance_score=0,
            geographic_score=0,
            topic_score=0,
            urgency_score=0,
            category_match_score=0,
            actionability_score=0,
            reasoning="Failed to parse",
            should_analyze=False
        )
```

---

## 📊 Agent 3: Impact Analyzer Agent

**Purpose**: Predict sales impact, quantify the opportunity/threat

**Output**:
- **Direction**: ⬆️ Increase / ⬇️ Decrease / ↔️ Neutral
- **Magnitude**: Low / Medium / High / Critical
- **Affected Products**: Specific SKUs or categories
- **Estimated Impact**: % change in sales, € value
- **Timeframe**: When impact will occur

### **Impact Analysis Framework**:

```python
from pydantic import BaseModel, Field
from typing import List, Literal
from datetime import datetime

class ProductImpact(BaseModel):
    """Impact on specific product/category"""
    product_or_category: str
    current_monthly_sales: float  # €
    predicted_change_pct: float  # e.g., +40% = 40.0
    predicted_change_euros: float  # €
    confidence: Literal["low", "medium", "high"]
    reasoning: str

class ImpactAnalysis(BaseModel):
    """Complete impact analysis for a news article"""
    article_title: str
    impact_direction: Literal["increase", "decrease", "neutral"]
    impact_magnitude: Literal["low", "medium", "high", "critical"]
    impact_timeframe: str  # "next 7 days", "next 30 days", "Q1 2025"
    affected_products: List[ProductImpact]
    overall_revenue_impact: float  # Total € impact
    confidence_score: float = Field(ge=0, le=1)
    risk_level: Literal["low", "medium", "high", "critical"]
    key_insights: List[str]
    supporting_evidence: List[str]

class ImpactAnalyzerAgent:
    """
    Predicts sales impact using historical data + LLM reasoning
    """

    def __init__(self, anthropic_client, sales_data: pd.DataFrame):
        self.client = anthropic_client
        self.sales_data = sales_data

        # Pre-calculate category baselines
        self.category_baselines = self._calculate_baselines()

    def _calculate_baselines(self) -> Dict:
        """
        Calculate historical sales patterns for each category
        This provides context for the LLM's predictions
        """
        baselines = {}

        # Group by department
        dept_sales = self.sales_data.groupby('Dept Fullname').agg({
            'Turnover': ['sum', 'mean', 'std'],
            'Qty Sold': 'sum',
            'Product': 'nunique'
        })

        for dept, row in dept_sales.iterrows():
            baselines[dept] = {
                'monthly_revenue': row[('Turnover', 'sum')] / 24,  # 2 years of data
                'volatility': row[('Turnover', 'std')],
                'products': row[('Product', 'nunique')]
            }

        return baselines

    def analyze_impact(self, scored_article: ScoredArticle) -> ImpactAnalysis:
        """
        Analyze potential sales impact of a news article
        """

        article = scored_article.article

        # Build context from historical data
        context = self._build_context()

        prompt = f"""
You are a retail pharmacy sales analyst with access to historical data.

NEWS ARTICLE:
Title: {article['title']}
Content: {article.get('content', article['description'])}
Published: {article['published_at']}

HISTORICAL SALES CONTEXT:
{context}

YOUR TASK:
Analyze how this news could impact sales. Consider:
1. Which product categories will be affected?
2. Will sales increase or decrease?
3. By what magnitude? (% and €)
4. When will the impact occur?
5. How confident are you?

Use the historical data as baselines. For example:
- If "flu outbreak" mentioned, OTC:Cold&Flu category typically sees 40-60% spike
- If "heatwave forecasted", sunscreen sales increase 80-120%
- If "competitor opens nearby", sales decrease 5-15% in affected location

Be specific and quantitative. Reference the baseline data.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            temperature=0.5,
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "predict_impact",
                "description": "Predict sales impact from news",
                "input_schema": ImpactAnalysis.schema()
            }]
        )

        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            impact = ImpactAnalysis(**tool_use.input, article_title=article['title'])
            return impact

        # Fallback
        return ImpactAnalysis(
            article_title=article['title'],
            impact_direction="neutral",
            impact_magnitude="low",
            impact_timeframe="unknown",
            affected_products=[],
            overall_revenue_impact=0.0,
            confidence_score=0.0,
            risk_level="low",
            key_insights=["Failed to analyze"],
            supporting_evidence=[]
        )

    def _build_context(self) -> str:
        """Build context from historical sales data"""

        # Format baselines for prompt
        context_lines = []

        # Top 5 categories by revenue
        top_categories = sorted(
            self.category_baselines.items(),
            key=lambda x: x[1]['monthly_revenue'],
            reverse=True
        )[:10]

        context_lines.append("TOP 10 PRODUCT CATEGORIES (Monthly Baseline):")
        for cat, data in top_categories:
            context_lines.append(
                f"  • {cat}: €{data['monthly_revenue']:,.0f}/month "
                f"({data['products']} products, volatility: €{data['volatility']:,.0f})"
            )

        # Add seasonal patterns if detected
        # Add known correlations (e.g., weather → sunscreen)

        return "\n".join(context_lines)
```

---

## 💡 Agent 4: Action Recommender Agent

**Purpose**: Generate specific, actionable recommendations

**Output**: Prioritized action items with deadlines

### **Action Types**:

1. **Inventory Actions**
   - Increase stock (how much, which SKUs)
   - Markdown slow movers
   - Emergency reorder

2. **Pricing Actions**
   - Promotional pricing
   - Competitive matching
   - Bundle offers

3. **Marketing Actions**
   - Email campaign
   - In-store displays
   - Social media posts

4. **Operational Actions**
   - Staff training
   - Store layout changes
   - Supplier negotiations

### **Implementation**:

```python
from pydantic import BaseModel
from typing import List, Literal

class Action(BaseModel):
    """Single actionable recommendation"""
    action_type: Literal["inventory", "pricing", "marketing", "operational"]
    priority: Literal["low", "medium", "high", "critical"]
    title: str
    description: str
    specific_steps: List[str]
    expected_benefit: str  # Quantified if possible
    deadline: str
    owner: str  # Who should execute
    estimated_effort: str  # "30 minutes", "2 hours", "1 day"

class ActionPlan(BaseModel):
    """Complete action plan for an impact"""
    article_title: str
    summary: str
    actions: List[Action]
    total_estimated_value: float  # € benefit if all actions executed
    quick_wins: List[str]  # Actions that can be done today

class ActionRecommenderAgent:
    """
    Generates specific, actionable recommendations
    """

    def __init__(self, anthropic_client):
        self.client = anthropic_client

    def recommend_actions(self, impact: ImpactAnalysis) -> ActionPlan:
        """Generate action plan based on impact analysis"""

        prompt = f"""
You are a retail operations consultant creating an action plan.

NEWS IMPACT ANALYSIS:
{impact.model_dump_json(indent=2)}

YOUR TASK:
Create a specific, actionable plan to capitalize on this opportunity or mitigate this threat.

For each action, specify:
- What exactly to do (specific products, quantities, prices)
- Who should do it (Buyer, Store Manager, Marketing, etc.)
- When it should be done (deadline)
- Expected benefit (quantified)
- How long it will take

Focus on actions that can be executed within the next 7-30 days.

Prioritize "quick wins" - high-impact actions that take <1 hour.

Example good action:
Title: "Emergency Reorder: Nurofen Rapid Relief"
Steps:
1. Contact Pharmax supplier (buyer: 10 min)
2. Order 1,500 units (delivery: 3 days)
3. Allocate 180 units to Baggot St (highest volume)
Expected Benefit: "Prevent €50,000 lost sales from stockout, maintain 50% margin"
Deadline: "Order by end of day today (Nov 15)"
Owner: "Head Buyer"
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2500,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "create_action_plan",
                "description": "Create actionable recommendations",
                "input_schema": ActionPlan.schema()
            }]
        )

        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            return ActionPlan(**tool_use.input, article_title=impact.article_title)

        return ActionPlan(
            article_title=impact.article_title,
            summary="No actions recommended",
            actions=[],
            total_estimated_value=0.0,
            quick_wins=[]
        )
```

---

## 🎛️ Orchestrator Agent

**Purpose**: Coordinate all agents, generate daily report

```python
from datetime import datetime
import json

class NewsAlertsOrchestrator:
    """
    Main orchestrator that runs daily and coordinates all agents
    """

    def __init__(self, config: Dict):
        self.config = config

        # Initialize all agents
        self.news_scout = NewsScoutAgent(config)
        self.relevance_filter = RelevanceFilterAgent(
            anthropic_client=config['anthropic_client'],
            product_categories=config['product_categories']
        )
        self.impact_analyzer = ImpactAnalyzerAgent(
            anthropic_client=config['anthropic_client'],
            sales_data=config['sales_data']
        )
        self.action_recommender = ActionRecommenderAgent(
            anthropic_client=config['anthropic_client']
        )

    def run_daily_analysis(self) -> Dict:
        """
        Main workflow: Run all agents in sequence
        """
        print(f"🚀 Starting daily news analysis - {datetime.now()}")

        # Step 1: Fetch news
        print("\n📰 Step 1: Fetching news...")
        raw_news = self.news_scout.fetch_daily_news()
        print(f"   Found {len(raw_news)} articles")

        # Step 2: Filter for relevance
        print("\n🎯 Step 2: Scoring relevance...")
        scored_articles = self.relevance_filter.score_articles(raw_news)
        print(f"   {len(scored_articles)} articles passed relevance filter")

        # Step 3: Analyze impact (top 10 most relevant)
        print("\n📊 Step 3: Analyzing impact...")
        impacts = []
        for article in scored_articles[:10]:  # Limit to top 10 to save API costs
            impact = self.impact_analyzer.analyze_impact(article)
            impacts.append(impact)

        # Filter for significant impacts
        significant_impacts = [
            imp for imp in impacts
            if imp.impact_magnitude in ["medium", "high", "critical"]
        ]
        print(f"   {len(significant_impacts)} significant impacts identified")

        # Step 4: Generate action plans
        print("\n💡 Step 4: Generating action plans...")
        action_plans = []
        for impact in significant_impacts:
            plan = self.action_recommender.recommend_actions(impact)
            action_plans.append(plan)

        # Step 5: Generate final report
        print("\n📋 Step 5: Generating daily report...")
        report = self._generate_report(
            raw_news_count=len(raw_news),
            relevant_count=len(scored_articles),
            impacts=significant_impacts,
            action_plans=action_plans
        )

        print(f"\n✅ Analysis complete! Generated {len(action_plans)} action plans")

        return report

    def _generate_report(self, **kwargs) -> Dict:
        """Generate final daily report"""

        report = {
            'date': datetime.now().isoformat(),
            'summary': {
                'total_articles_scanned': kwargs['raw_news_count'],
                'relevant_articles': kwargs['relevant_count'],
                'significant_impacts': len(kwargs['impacts']),
                'action_plans': len(kwargs['action_plans'])
            },
            'impacts': [imp.model_dump() for imp in kwargs['impacts']],
            'action_plans': [plan.model_dump() for plan in kwargs['action_plans']],
            'quick_wins': self._extract_quick_wins(kwargs['action_plans']),
            'critical_alerts': self._extract_critical_alerts(kwargs['impacts'])
        }

        # Save to JSON
        filename = f"daily_alerts_{datetime.now().strftime('%Y%m%d')}.json"
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        # Generate human-readable summary
        self._generate_email_summary(report)

        return report

    def _extract_quick_wins(self, action_plans: List[ActionPlan]) -> List[str]:
        """Extract all quick wins across plans"""
        quick_wins = []
        for plan in action_plans:
            quick_wins.extend(plan.quick_wins)
        return quick_wins

    def _extract_critical_alerts(self, impacts: List[ImpactAnalysis]) -> List[Dict]:
        """Extract critical/high severity impacts"""
        critical = [
            {
                'title': imp.article_title,
                'magnitude': imp.impact_magnitude,
                'revenue_impact': imp.overall_revenue_impact,
                'timeframe': imp.impact_timeframe
            }
            for imp in impacts
            if imp.impact_magnitude in ["high", "critical"]
        ]
        return critical

    def _generate_email_summary(self, report: Dict):
        """Generate human-readable email summary"""

        # Generate HTML email or Slack message
        # This would be sent to operations team

        pass  # Implement based on your needs
```

---

## 📅 Daily Scheduling

### **Option 1: Cron Job (Linux/Mac)**

```bash
# Run daily at 7 AM
0 7 * * * cd /path/to/project && python run_daily_alerts.py
```

### **Option 2: GitHub Actions (Cloud)**

```yaml
# .github/workflows/daily-alerts.yml
name: Daily News Alerts

on:
  schedule:
    - cron: '0 7 * * *'  # 7 AM UTC daily

jobs:
  run-alerts:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run daily analysis
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          NEWSAPI_KEY: ${{ secrets.NEWSAPI_KEY }}
        run: python run_daily_alerts.py
      - name: Upload report
        uses: actions/upload-artifact@v3
        with:
          name: daily-report
          path: daily_alerts_*.json
```

### **Option 3: Cloud Functions (AWS Lambda, Google Cloud Functions)**

```python
# AWS Lambda handler
def lambda_handler(event, context):
    orchestrator = NewsAlertsOrchestrator(config)
    report = orchestrator.run_daily_analysis()

    # Send to S3, send email, post to Slack, etc.

    return {
        'statusCode': 200,
        'body': json.dumps(report)
    }
```

---

## 💰 Cost Estimation

### **API Costs (Monthly)**:

**NewsAPI** (Free tier):
- 100 requests/day = 3,000/month
- ✅ FREE

**Anthropic Claude** (Usage-based):
- Assume 10 articles/day analyzed
- Each article: ~2,000 input tokens, ~1,000 output tokens
- 10 articles × 3,000 tokens × 30 days = 900,000 tokens/month
- Cost: ~$5-10/month (Sonnet 3.5)
- ✅ CHEAP

**Total Monthly Cost**: ~$10-15/month

**ROI**: If system prevents ONE stockout or catches ONE trend early → $50,000+ value

---

## 🎨 Dashboard UI Options

### **Option 1: Simple HTML Email**
```html
<!DOCTYPE html>
<html>
<body>
  <h1>📰 Daily Retail Alerts - November 15, 2025</h1>

  <div style="background: #ff0000; padding: 20px; color: white;">
    <h2>🚨 CRITICAL ALERT</h2>
    <p><strong>Flu Outbreak Reported in Dublin</strong></p>
    <p>Impact: +40% sales increase expected in OTC:Cold&Flu</p>
    <p>Action: Emergency reorder Benylin, Nurofen, Lemsip</p>
  </div>

  <!-- More alerts... -->
</body>
</html>
```

### **Option 2: Streamlit Dashboard**
```python
import streamlit as st

st.title("📰 Daily Retail News Alerts")

# Show critical alerts first
st.header("🚨 Critical Alerts")
for alert in critical_alerts:
    with st.expander(alert['title']):
        st.metric("Revenue Impact", f"€{alert['revenue_impact']:,}")
        st.write(alert['description'])

# Show all impacts
st.header("📊 All Impacts")
df = pd.DataFrame(impacts)
st.dataframe(df)

# Show action items
st.header("💡 Recommended Actions")
for action in actions:
    st.checkbox(action['title'], key=action['id'])
```

### **Option 3: Slack Bot**
```python
import slack_sdk

def send_to_slack(report):
    client = slack_sdk.WebClient(token=SLACK_TOKEN)

    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "📰 Daily Retail Alerts"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{len(critical_alerts)} critical alerts* | {len(action_plans)} action plans"
                }
            }
            # ... more blocks
        ]
    }

    client.chat_postMessage(channel="#retail-ops", **message)
```

---

## ⚠️ Common Pitfalls & Solutions

### **Pitfall 1: Too Many False Positives**
❌ System alerts on irrelevant news
✅ **Solution**: Stricter relevance filtering, feedback loop

### **Pitfall 2: Hallucinated Impact Predictions**
❌ LLM predicts "+200% sales" with no basis
✅ **Solution**: Ground predictions in historical data, add confidence scores

### **Pitfall 3: Alert Fatigue**
❌ Team ignores daily emails because too many alerts
✅ **Solution**: Only send critical/high priority, weekly digest for lower priority

### **Pitfall 4: No Action Taken**
❌ Great alerts but nobody acts on them
✅ **Solution**: Integrate with existing workflows (auto-create Jira tickets, Slack reminders)

### **Pitfall 5: Stale News**
❌ System catches news 3 days late
✅ **Solution**: Run multiple times per day, integrate real-time sources (Twitter)

---

## 🚀 Phased Implementation Plan

### **Phase 1: MVP (Week 1)**
- ✅ News Scout Agent (NewsAPI only)
- ✅ Simple rule-based filtering
- ✅ Email summary (no LLM analysis yet)
- **Goal**: Prove concept, get feedback

### **Phase 2: AI Analysis (Week 2)**
- ✅ Add Relevance Filter Agent (with LLM)
- ✅ Add Impact Analyzer Agent
- ✅ Structured outputs, scoring
- **Goal**: Intelligent filtering and impact prediction

### **Phase 3: Actionable Recommendations (Week 3)**
- ✅ Add Action Recommender Agent
- ✅ Integrate with inventory data
- ✅ Generate specific action items
- **Goal**: Make alerts actionable, not just informational

### **Phase 4: Production Polish (Week 4)**
- ✅ Better UI (Streamlit/Slack)
- ✅ Feedback loop (mark alerts as useful/not useful)
- ✅ Performance optimization
- **Goal**: Production-ready system

---

## 📚 Recommended Tech Stack

```
Core:
- Python 3.11+
- Anthropic Claude API (Sonnet 3.5)
- Pydantic (structured outputs)

Data Sources:
- NewsAPI
- Google News RSS (feedparser)
- OpenWeather API
- PyTrends (Google Trends)

Storage:
- SQLite (for storing historical alerts)
- JSON files (daily reports)

Scheduling:
- APScheduler (Python scheduler)
- OR GitHub Actions (cloud)

UI:
- Streamlit (dashboard)
- OR Slack API (notifications)
- OR Email (SendGrid, AWS SES)

Optional:
- LangChain (agent orchestration)
- CrewAI (multi-agent framework)
- Redis (caching API responses)
```

---

## 🎯 Success Metrics

Track these to measure effectiveness:

1. **Alert Quality**
   - % of alerts acted upon
   - False positive rate (<20% target)
   - Time from alert to action

2. **Business Impact**
   - Revenue captured from early trend detection
   - Stockouts prevented
   - Successful promotional campaigns launched

3. **Operational Efficiency**
   - Time saved (vs manual news monitoring)
   - Number of quick wins executed
   - Reduction in reactive decision-making

4. **System Performance**
   - Daily runtime (target: <5 minutes)
   - API costs per month
   - System uptime

---

## 💬 Final Recommendations

**DO**:
✅ Start with MVP - prove value before building complex system
✅ Use structured outputs (Pydantic) to prevent hallucination
✅ Ground LLM predictions in real historical data
✅ Make alerts actionable with specific next steps
✅ Integrate with existing workflows (don't create new work)
✅ Get feedback loop - track which alerts led to action

**DON'T**:
❌ Try to analyze every news article (too expensive, noisy)
❌ Trust LLM predictions without validation
❌ Send alerts without recommended actions
❌ Build complex UI before proving value
❌ Ignore false positives (kills trust)

**KEY INSIGHT**:
The value is NOT in reading more news - it's in catching the 2-3 critical signals per week that actually impact your business, BEFORE your competitors do.

Focus on precision over recall. Better to catch 3/5 critical events than to generate 100 alerts where 95 are noise.

---

Want me to start building a prototype? I can create:
1. **MVP Python script** (runs in 30 seconds, outputs simple report)
2. **Full multi-agent system** (production-ready)
3. **Specific agent** (e.g., just the Impact Analyzer)

Let me know what would be most helpful! 🚀
