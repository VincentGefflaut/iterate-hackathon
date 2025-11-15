# AI News Alerts for Black Swan Events
## LLM as Context-Aware Event Detector, NOT Forecaster

---

## 🎯 Correct Mental Model

### ❌ **WRONG Approach** (What I Suggested Before):
```
News → LLM predicts "+40% sales increase" → Action
```
**Problem**: LLM is guessing, hallucinating numbers, no basis in reality.

### ✅ **RIGHT Approach** (Event Detection + Context Matching):
```
News → LLM detects event type → Matches to known patterns in YOUR data → Binary alert (YES/NO)
```

**The LLM's Job**:
- Detect: "Taylor Swift concert announced in Dublin, June 15-17"
- Classify: This is a "Major Event" type
- Context: You have 10 stores in Dublin
- Alert: YES - "Major event detected near your locations"

**NOT the LLM's Job**:
- Predicting "+37% sales increase" (bullshit)
- Forecasting which products will sell more (data science job)

---

## 🦢 Black Swan Event Categories

The LLM should detect **external events** that your internal forecasting models don't see:

### **1. Major Events**
Events bringing large crowds to the area:
- Concerts (Taylor Swift, Ed Sheeran at 3Arena)
- Sporting events (Ireland rugby, GAA finals at Croke Park)
- Festivals (St. Patrick's Day, Dublin Pride)
- Conferences (Web Summit brings 70,000 people)

**LLM Task**: Detect event + extract (date, location, expected attendance)
**Your Response**: Check if near your stores → stock travel essentials, pain relief, energy products

### **2. Health Emergencies**
Sudden health-related events:
- Disease outbreaks (flu, norovirus)
- Food poisoning incidents
- Pollen/allergy alerts
- Air quality warnings

**LLM Task**: Detect health threat + severity + affected area
**Your Response**: Pre-defined playbook (e.g., flu outbreak → stock Tamiflu, hand sanitizer)

### **3. Weather Extremes**
Unusual weather (not regular forecasts):
- Heatwaves (>28°C for 3+ days)
- Cold snaps (<0°C)
- Storm warnings (Met Éireann red alerts)
- Flooding

**LLM Task**: Detect extreme weather + dates
**Your Response**: Playbook-based (heatwave → sunscreen, cold snap → cold/flu meds)

### **4. Economic/Market Shocks**
- Currency crashes
- Bank failures
- Major company layoffs in Dublin
- Tax changes affecting consumers

**LLM Task**: Detect shock + severity
**Your Response**: Could affect discretionary spending (vitamins, skincare)

### **5. Competitor Actions**
- New pharmacy opening near your locations
- Major promotion by competitor
- Competitor closing location

**LLM Task**: Detect + extract location
**Your Response**: Check proximity to your stores → defensive strategy

### **6. Regulatory/Legal Changes**
- Prescription drug reclassifications (Rx → OTC)
- New health regulations
- Tax changes on products

**LLM Task**: Detect change + effective date + affected products
**Your Response**: Operational changes needed

### **7. Supply Chain Disruptions**
- Supplier bankruptcy
- Port strikes
- Transportation issues
- Product recalls

**LLM Task**: Detect disruption + affected products/suppliers
**Your Response**: Check if you use that supplier → find alternatives

### **8. Viral Trends/Media Buzz**
- Celebrity health scare (everyone rushes to buy supplements they mentioned)
- Viral TikTok product
- Health scare in media (e.g., "talc powder cancer risk")

**LLM Task**: Detect viral moment + product mentioned
**Your Response**: Check if you stock it → prepare for surge or questions

---

## 🏗️ Refined Architecture

### **Simple 2-Agent System**

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│  (Runs daily, coordinates agents, generates alerts)        │
└──────────────┬──────────────────────────────────────────────┘
               │
        ┌──────┴──────┐
        │             │
        ▼             ▼
┌──────────────┐ ┌──────────────────┐
│ EVENT        │ │ CONTEXT          │
│ DETECTOR     │ │ MATCHER          │
│ AGENT        │ │ AGENT            │
└──────────────┘ └──────────────────┘
Detects black    Matches events to
swan events      your business data
from news        → Binary YES/NO alert
```

---

## 🔍 Agent 1: Event Detector

**Job**: Scan news and extract structured event data (NOT predict impact!)

### **Structured Output**:

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime

class DetectedEvent(BaseModel):
    """Structured event extracted from news"""

    # Event classification
    event_type: Literal[
        "major_event",        # Concert, festival, conference
        "health_emergency",   # Outbreak, alert
        "weather_extreme",    # Heatwave, storm
        "economic_shock",     # Market crash, layoffs
        "competitor_action",  # New store, promo
        "regulatory_change",  # Law changes
        "supply_disruption",  # Supplier issues
        "viral_trend",        # Social media buzz
        "other"
    ]

    # Event details
    title: str
    description: str
    severity: Literal["low", "medium", "high", "critical"]

    # Time & location
    event_date: Optional[str] = None  # When it happens/happened
    location: Optional[str] = None    # Where (Dublin, Ireland, specific area)
    duration: Optional[str] = None    # How long (e.g., "3 days", "ongoing")

    # Specifics
    affected_products: List[str] = []  # Product types mentioned (not quantities!)
    affected_areas: List[str] = []     # Geographic areas
    expected_attendance: Optional[int] = None  # For events
    named_entities: List[str] = []     # Companies, people, brands mentioned

    # Metadata
    source_url: str
    published_at: str
    confidence: Literal["low", "medium", "high"]
    urgency: Literal["immediate", "within_week", "within_month", "low"]

    # Key facts (NO predictions!)
    key_facts: List[str] = []
    potential_relevance: str  # Why this might matter to retail pharmacy

class EventDetectorAgent:
    """
    Detects black swan events from news
    ONLY extracts facts, NO predictions
    """

    def __init__(self, anthropic_client):
        self.client = anthropic_client

    def detect_events(self, articles: List[Dict]) -> List[DetectedEvent]:
        """
        Process news articles and extract events

        Returns ONLY events that match the categories we care about
        """
        detected_events = []

        for article in articles:
            event = self._analyze_article(article)

            # Only keep if it's a real event (not "other")
            if event and event.event_type != "other":
                detected_events.append(event)

        return detected_events

    def _analyze_article(self, article: Dict) -> Optional[DetectedEvent]:
        """Analyze single article for events"""

        prompt = f"""
You are an event detection system for a retail pharmacy chain in Dublin, Ireland.

Your ONLY job is to detect external events from news that could affect a retail pharmacy business.

NEWS ARTICLE:
Title: {article['title']}
Content: {article.get('content', article.get('description', ''))}
Published: {article['published_at']}
URL: {article['url']}

YOUR TASK:
Determine if this article describes a BLACK SWAN EVENT in one of these categories:

1. MAJOR EVENT: Concert, festival, conference, sporting event bringing crowds to Dublin
   - Extract: date, location, expected attendance
   - Example: "Taylor Swift concert at 3Arena, June 15"

2. HEALTH EMERGENCY: Outbreak, disease alert, food poisoning, air quality warning
   - Extract: what, where, severity
   - Example: "Norovirus outbreak in Dublin hospitals"

3. WEATHER EXTREME: Heatwave, storm, flooding (EXTREME only, not normal weather)
   - Extract: what, when, affected areas
   - Example: "Met Éireann red alert: Storm approaching"

4. ECONOMIC SHOCK: Currency crash, major layoffs, bank failure
   - Extract: what happened, scale
   - Example: "Major tech company lays off 5,000 in Dublin"

5. COMPETITOR ACTION: New pharmacy opening, major competitor promo, competitor closing
   - Extract: competitor name, location, what they're doing
   - Example: "Boots opening mega-store in Dundrum"

6. REGULATORY CHANGE: Drug reclassifications, health regulations, tax changes
   - Extract: what changed, when effective, what products
   - Example: "Pantoprazole moves from prescription to OTC"

7. SUPPLY DISRUPTION: Supplier bankruptcy, strikes, transportation issues, recalls
   - Extract: what's disrupted, which suppliers/products
   - Example: "Port strike delays shipments from EU"

8. VIRAL TREND: Celebrity health scare, TikTok product going viral, media health scare
   - Extract: what product, why trending
   - Example: "Ozempic searches surge after celebrity mention"

CRITICAL RULES:
- If the article doesn't describe any of these event types, return NULL
- Extract ONLY facts from the article - NO predictions, NO guessing
- Do NOT predict sales impact or quantities
- Do NOT add information not in the article
- Focus on events in Ireland/Dublin (but include major global events if severe)

Example GOOD extraction:
{
  "event_type": "major_event",
  "title": "Taylor Swift Concert Announced",
  "event_date": "2025-06-15 to 2025-06-17",
  "location": "3Arena, Dublin",
  "expected_attendance": 45000,
  "key_facts": [
    "Three-night concert",
    "June 15-17, 2025",
    "Tickets selling out fast",
    "Expected 15,000 per night"
  ],
  "potential_relevance": "Major influx of visitors to Dublin area. Stores near 3Arena may see increased foot traffic."
}

Example BAD extraction (DON'T DO THIS):
{
  "event_type": "major_event",
  "title": "Concert announced",
  "predicted_sales_increase": "+35%",  ← NO! Don't predict
  "recommended_stock": "500 units"     ← NO! Don't recommend
}

Analyze this article and extract the event if it matches our categories.
"""

        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1500,
            temperature=0.2,  # Low temp for factual extraction
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "extract_event",
                "description": "Extract structured event from article",
                "input_schema": DetectedEvent.schema()
            }]
        )

        # Parse structured output
        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            try:
                event = DetectedEvent(**tool_use.input)
                return event
            except:
                return None

        return None
```

---

## 🎯 Agent 2: Context Matcher

**Job**: Take detected events and match them against YOUR business data to decide: Alert or Not?

This is where your **domain knowledge** comes in, not LLM predictions.

```python
from typing import List, Tuple
import pandas as pd
from datetime import datetime, timedelta

class BusinessContext:
    """Your business data and rules"""

    def __init__(self, sales_data: pd.DataFrame, inventory: pd.DataFrame, locations: List[Dict]):
        self.sales_data = sales_data
        self.inventory = inventory
        self.locations = locations

        # Pre-compute useful facts
        self.location_coords = self._get_location_coordinates()
        self.product_categories = self._get_product_categories()
        self.historical_patterns = self._analyze_historical_patterns()

    def _get_location_coordinates(self) -> Dict:
        """Map of your store locations"""
        return {
            'Baggot St': {'lat': 53.3315, 'lon': -6.2449, 'area': 'Dublin 4'},
            'Churchtown': {'lat': 53.3089, 'lon': -6.2881, 'area': 'Dublin 14'},
            'Barrow St': {'lat': 53.3418, 'lon': -6.2394, 'area': 'Dublin 2'},
            # ... all locations
        }

    def _get_product_categories(self) -> Dict:
        """Product categories you stock"""
        categories = self.sales_data.groupby('Dept Fullname').agg({
            'Product': 'nunique',
            'Turnover': 'sum'
        })
        return categories.to_dict('index')

    def _analyze_historical_patterns(self) -> Dict:
        """Known patterns from YOUR data"""
        patterns = {}

        # Example: Flu season pattern (from your actual data)
        flu_products = self.sales_data[
            self.sales_data['Dept Fullname'] == 'OTC : Cold & Flu'
        ]

        # Calculate baseline vs peak
        monthly_flu_sales = flu_products.groupby(
            flu_products['Sale Date'].dt.to_period('M')
        )['Turnover'].sum()

        patterns['flu_season'] = {
            'baseline_monthly': monthly_flu_sales.quantile(0.5),
            'peak_monthly': monthly_flu_sales.quantile(0.95),
            'peak_vs_baseline': monthly_flu_sales.quantile(0.95) / monthly_flu_sales.quantile(0.5)
        }

        # More patterns...
        # Heatwave → sunscreen pattern
        # Event → travel essentials pattern
        # etc.

        return patterns

class Alert(BaseModel):
    """Binary alert with context"""
    alert: bool  # YES or NO
    event: DetectedEvent
    reason: str
    affected_locations: List[str]
    relevant_products: List[str]
    historical_context: str  # What YOUR data says
    suggested_playbook: str  # Pre-defined action template
    urgency: Literal["immediate", "within_24h", "within_week", "low"]

class ContextMatcherAgent:
    """
    Matches detected events against business context
    Generates binary YES/NO alerts
    """

    def __init__(self, business_context: BusinessContext):
        self.context = business_context

    def evaluate_events(self, events: List[DetectedEvent]) -> List[Alert]:
        """
        For each event, decide: Should we alert?

        Uses business rules + context, NOT predictions
        """
        alerts = []

        for event in events:
            alert = self._evaluate_single_event(event)
            if alert.alert:  # Only keep YES alerts
                alerts.append(alert)

        # Sort by urgency
        alerts.sort(key=lambda x: {
            'immediate': 0,
            'within_24h': 1,
            'within_week': 2,
            'low': 3
        }[x.urgency])

        return alerts

    def _evaluate_single_event(self, event: DetectedEvent) -> Alert:
        """
        Evaluate single event against business context

        Returns Alert with YES/NO decision
        """

        # Route to appropriate evaluator based on event type
        evaluators = {
            'major_event': self._evaluate_major_event,
            'health_emergency': self._evaluate_health_emergency,
            'weather_extreme': self._evaluate_weather_extreme,
            'competitor_action': self._evaluate_competitor_action,
            'supply_disruption': self._evaluate_supply_disruption,
            'regulatory_change': self._evaluate_regulatory_change,
            'viral_trend': self._evaluate_viral_trend,
            'economic_shock': self._evaluate_economic_shock,
        }

        evaluator = evaluators.get(event.event_type)
        if evaluator:
            return evaluator(event)
        else:
            # Unknown type, no alert
            return Alert(
                alert=False,
                event=event,
                reason="Event type not handled",
                affected_locations=[],
                relevant_products=[],
                historical_context="",
                suggested_playbook="",
                urgency="low"
            )

    def _evaluate_major_event(self, event: DetectedEvent) -> Alert:
        """
        Evaluate major event (concert, festival, conference)

        Logic:
        1. Is event near our locations? (<2km)
        2. Is it large enough to matter? (>5,000 people)
        3. Is it soon? (within 30 days)
        """

        # Extract event location
        event_location = event.location

        # Check proximity to our stores
        affected_stores = self._find_nearby_stores(event_location, radius_km=2)

        # Check size
        is_large = event.expected_attendance and event.expected_attendance > 5000

        # Check timing
        is_soon = self._is_within_days(event.event_date, days=30)

        # Decision
        should_alert = len(affected_stores) > 0 and is_large and is_soon

        if should_alert:
            # Determine relevant products (from YOUR data)
            # Events → travel essentials, pain relief, energy
            relevant_products = [
                'Travel toiletries',
                'Pain relief (Nurofen, Paracetamol)',
                'Energy drinks/snacks',
                'Plasters/first aid',
                'Hand sanitizer'
            ]

            return Alert(
                alert=True,
                event=event,
                reason=f"Large event ({event.expected_attendance:,} people) near {len(affected_stores)} of our stores",
                affected_locations=[s for s in affected_stores],
                relevant_products=relevant_products,
                historical_context=self._get_event_historical_context(),
                suggested_playbook="MAJOR_EVENT_PLAYBOOK",
                urgency="within_week" if is_soon else "low"
            )
        else:
            return Alert(
                alert=False,
                event=event,
                reason="Event not near our locations or too small/far in future",
                affected_locations=[],
                relevant_products=[],
                historical_context="",
                suggested_playbook="",
                urgency="low"
            )

    def _evaluate_health_emergency(self, event: DetectedEvent) -> Alert:
        """
        Evaluate health emergency (flu outbreak, norovirus, etc.)

        Logic:
        1. Is it in Ireland/Dublin?
        2. What's the severity?
        3. Do we stock relevant products?
        """

        # Check location
        is_local = event.location and ('ireland' in event.location.lower() or 'dublin' in event.location.lower())

        # Check severity
        is_severe = event.severity in ['high', 'critical']

        # Map to product categories
        product_mapping = {
            'flu': 'OTC : Cold & Flu',
            'norovirus': 'OTC : GIT',
            'covid': 'OTC : Cold & Flu',
            'allergy': 'OTC : Allergy',
            'food poisoning': 'OTC : GIT'
        }

        # Find relevant category
        relevant_category = None
        for keyword, category in product_mapping.items():
            if keyword in event.description.lower() or keyword in event.title.lower():
                relevant_category = category
                break

        should_alert = is_local and is_severe and relevant_category

        if should_alert:
            # Get historical context from YOUR data
            historical_context = self.context.historical_patterns.get('flu_season', {})

            return Alert(
                alert=True,
                event=event,
                reason=f"Health emergency in our area affecting {relevant_category}",
                affected_locations=list(self.context.location_coords.keys()),  # All locations
                relevant_products=[relevant_category],
                historical_context=f"Historical pattern: Peak demand is {historical_context.get('peak_vs_baseline', 'N/A')}x baseline",
                suggested_playbook="HEALTH_EMERGENCY_PLAYBOOK",
                urgency="immediate" if event.severity == "critical" else "within_24h"
            )
        else:
            return Alert(
                alert=False,
                event=event,
                reason="Not severe enough or not in our area",
                affected_locations=[],
                relevant_products=[],
                historical_context="",
                suggested_playbook="",
                urgency="low"
            )

    def _evaluate_weather_extreme(self, event: DetectedEvent) -> Alert:
        """
        Evaluate extreme weather

        Logic:
        1. Is it actually extreme? (not normal weather)
        2. When is it happening?
        3. What products are affected?
        """

        # Map weather to products (from YOUR knowledge)
        weather_product_map = {
            'heatwave': ['Sunscreen', 'Hydration products', 'Insect repellent'],
            'cold snap': ['OTC : Cold & Flu', 'Hot water bottles', 'Lip balm'],
            'storm': ['Batteries', 'First aid', 'Candles'],
            'high pollen': ['OTC : Allergy', 'Antihistamines', 'Eye drops']
        }

        # Detect weather type
        weather_type = None
        event_lower = event.title.lower() + ' ' + event.description.lower()

        for weather, products in weather_product_map.items():
            if weather in event_lower:
                weather_type = weather
                relevant_products = products
                break

        # Check timing
        is_imminent = self._is_within_days(event.event_date, days=7)

        should_alert = weather_type and is_imminent and event.severity in ['high', 'critical']

        if should_alert:
            return Alert(
                alert=True,
                event=event,
                reason=f"Extreme weather ({weather_type}) approaching",
                affected_locations=list(self.context.location_coords.keys()),
                relevant_products=relevant_products,
                historical_context=self._get_weather_historical_context(weather_type),
                suggested_playbook=f"WEATHER_{weather_type.upper()}_PLAYBOOK",
                urgency="within_24h" if is_imminent else "within_week"
            )
        else:
            return Alert(
                alert=False,
                event=event,
                reason="Not extreme enough or too far in future",
                affected_locations=[],
                relevant_products=[],
                historical_context="",
                suggested_playbook="",
                urgency="low"
            )

    def _evaluate_competitor_action(self, event: DetectedEvent) -> Alert:
        """
        Evaluate competitor action (new store, promotion, etc.)
        """

        # Check if near our locations
        affected_stores = self._find_nearby_stores(event.location, radius_km=1)

        should_alert = len(affected_stores) > 0 and event.severity in ['medium', 'high', 'critical']

        if should_alert:
            return Alert(
                alert=True,
                event=event,
                reason=f"Competitor action near {len(affected_stores)} of our stores",
                affected_locations=affected_stores,
                relevant_products=["All categories"],
                historical_context="Competitive threat requires response",
                suggested_playbook="COMPETITOR_RESPONSE_PLAYBOOK",
                urgency="within_week"
            )
        else:
            return Alert(alert=False, event=event, reason="Not near our locations",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

    def _evaluate_supply_disruption(self, event: DetectedEvent) -> Alert:
        """
        Evaluate supply chain disruption

        Check if we use affected suppliers
        """

        # Check if any of our suppliers mentioned
        our_suppliers = self.sales_data['OrderList'].unique()

        affected_suppliers = []
        for supplier in our_suppliers:
            if supplier.lower() in event.description.lower():
                affected_suppliers.append(supplier)

        should_alert = len(affected_suppliers) > 0

        if should_alert:
            # Find products from affected suppliers
            affected_products = self.sales_data[
                self.sales_data['OrderList'].isin(affected_suppliers)
            ]['Product'].unique().tolist()[:20]  # Limit to top 20

            return Alert(
                alert=True,
                event=event,
                reason=f"Supply disruption affects {len(affected_suppliers)} of our suppliers",
                affected_locations=list(self.context.location_coords.keys()),
                relevant_products=affected_products,
                historical_context=f"Suppliers affected: {', '.join(affected_suppliers)}",
                suggested_playbook="SUPPLY_DISRUPTION_PLAYBOOK",
                urgency="immediate"
            )
        else:
            return Alert(alert=False, event=event, reason="Doesn't affect our suppliers",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

    def _evaluate_regulatory_change(self, event: DetectedEvent) -> Alert:
        """
        Evaluate regulatory changes affecting products
        """

        # Check if any products we stock are mentioned
        our_products = set(self.sales_data['Product'].str.lower().unique())

        mentioned_products = []
        for product in event.affected_products:
            # Fuzzy match
            product_lower = product.lower()
            if any(product_lower in our_prod or our_prod in product_lower for our_prod in our_products):
                mentioned_products.append(product)

        should_alert = len(mentioned_products) > 0

        if should_alert:
            return Alert(
                alert=True,
                event=event,
                reason=f"Regulatory change affects {len(mentioned_products)} products we stock",
                affected_locations=list(self.context.location_coords.keys()),
                relevant_products=mentioned_products,
                historical_context="Regulatory compliance required",
                suggested_playbook="REGULATORY_CHANGE_PLAYBOOK",
                urgency="within_week"
            )
        else:
            return Alert(alert=False, event=event, reason="Doesn't affect our products",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

    def _evaluate_viral_trend(self, event: DetectedEvent) -> Alert:
        """
        Evaluate viral trend (celebrity mention, TikTok viral, etc.)
        """

        # Check if we stock the trending product
        trending_product = event.affected_products[0] if event.affected_products else None

        if not trending_product:
            return Alert(alert=False, event=event, reason="No specific product mentioned",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

        # Check our inventory
        have_product = trending_product.lower() in ' '.join(self.sales_data['Product'].str.lower())

        should_alert = have_product and event.severity in ['medium', 'high', 'critical']

        if should_alert:
            # Check current stock levels
            stock_level = self._get_stock_level(trending_product)

            return Alert(
                alert=True,
                event=event,
                reason=f"Viral trend for product we stock: {trending_product}",
                affected_locations=list(self.context.location_coords.keys()),
                relevant_products=[trending_product],
                historical_context=f"Current stock: {stock_level}",
                suggested_playbook="VIRAL_TREND_PLAYBOOK",
                urgency="immediate"
            )
        else:
            return Alert(alert=False, event=event, reason="We don't stock this product",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

    def _evaluate_economic_shock(self, event: DetectedEvent) -> Alert:
        """
        Evaluate economic shock

        Less actionable but good to know
        """

        should_alert = event.severity in ['high', 'critical']

        if should_alert:
            return Alert(
                alert=True,
                event=event,
                reason="Major economic event may affect consumer spending",
                affected_locations=list(self.context.location_coords.keys()),
                relevant_products=["Discretionary items (vitamins, skincare)"],
                historical_context="Monitor sales trends closely",
                suggested_playbook="ECONOMIC_UNCERTAINTY_PLAYBOOK",
                urgency="within_week"
            )
        else:
            return Alert(alert=False, event=event, reason="Not severe enough",
                        affected_locations=[], relevant_products=[], historical_context="",
                        suggested_playbook="", urgency="low")

    # Helper methods
    def _find_nearby_stores(self, location: str, radius_km: float) -> List[str]:
        """Find stores within radius of event location"""
        # Simplified - in reality use geopy or similar
        if not location:
            return []

        location_lower = location.lower()
        nearby = []

        for store, coords in self.context.location_coords.items():
            area = coords['area'].lower()
            if area in location_lower or location_lower in area:
                nearby.append(store)

        return nearby

    def _is_within_days(self, event_date: str, days: int) -> bool:
        """Check if event is within N days"""
        if not event_date:
            return False

        try:
            # Parse various date formats
            from dateutil import parser
            event_dt = parser.parse(event_date)
            days_until = (event_dt - datetime.now()).days
            return 0 <= days_until <= days
        except:
            return False

    def _get_stock_level(self, product_name: str) -> str:
        """Get current stock level for product"""
        # Query inventory data
        matching = self.context.inventory[
            self.context.inventory['Product'].str.contains(product_name, case=False, na=False)
        ]

        if len(matching) > 0:
            total_stock = matching['Branch Stock Level'].sum()
            return f"{total_stock:.0f} units across all locations"
        else:
            return "Not in current inventory"

    def _get_event_historical_context(self) -> str:
        """Get historical context for major events"""
        # From your data, you might know:
        # "Last year's concert weekend saw +25% foot traffic in nearby stores"
        return "Historical data shows events increase foot traffic 15-30%"

    def _get_weather_historical_context(self, weather_type: str) -> str:
        """Get historical weather impact from YOUR data"""
        # Example: Query sales data for last heatwave
        # "During July 2024 heatwave, sunscreen sales increased 2.8x"
        return f"Historical {weather_type} events show significant category impact"
```

---

## 📋 Playbooks (Pre-Defined Actions)

Instead of LLM generating actions, use **playbooks** - pre-defined responses:

```python
PLAYBOOKS = {
    "MAJOR_EVENT_PLAYBOOK": {
        "title": "Major Event Response",
        "actions": [
            "Check inventory of travel essentials at affected locations",
            "Increase staffing at nearby stores during event dates",
            "Prepare promotional bundles (travel size products)",
            "Ensure adequate stock of pain relief, energy products",
            "Communicate with store managers about expected traffic"
        ],
        "timeline": "Execute 5-7 days before event",
        "owner": "Operations Manager"
    },

    "HEALTH_EMERGENCY_PLAYBOOK": {
        "title": "Health Emergency Response",
        "actions": [
            "Emergency stock check of relevant OTC medications",
            "Contact suppliers for emergency reorder if needed",
            "Brief pharmacy staff on expected customer questions",
            "Prepare customer communications (posters, website)",
            "Monitor stock levels daily during emergency"
        ],
        "timeline": "Execute immediately",
        "owner": "Head Pharmacist + Buyers"
    },

    "WEATHER_HEATWAVE_PLAYBOOK": {
        "title": "Heatwave Preparation",
        "actions": [
            "Stock check: Sunscreen, hydration products, insect repellent",
            "Move sun care products to prominent display",
            "Order additional stock if needed (lead time: 3-5 days)",
            "Train staff on sun safety recommendations",
            "Prepare promotional bundles (sunscreen + aftersun)"
        ],
        "timeline": "Execute 3-5 days before heatwave",
        "owner": "Category Manager + Store Managers"
    },

    "COMPETITOR_RESPONSE_PLAYBOOK": {
        "title": "Competitive Response",
        "actions": [
            "Assess competitor's offering (visit new store, review promo)",
            "Price check key products vs competitor",
            "Prepare defensive promotions if needed",
            "Review customer service quality at affected locations",
            "Consider loyalty program enhancements"
        ],
        "timeline": "Execute within 2 weeks",
        "owner": "Operations Director"
    },

    "SUPPLY_DISRUPTION_PLAYBOOK": {
        "title": "Supply Chain Disruption Response",
        "actions": [
            "Identify all products from affected supplier",
            "Check current stock levels of affected products",
            "Contact alternative suppliers for pricing/availability",
            "Communicate delays to stores if stockouts expected",
            "Consider temporary substitutions"
        ],
        "timeline": "Execute immediately",
        "owner": "Head Buyer"
    },

    "VIRAL_TREND_PLAYBOOK": {
        "title": "Viral Trend Capture",
        "actions": [
            "Emergency stock check of trending product",
            "Order maximum available quantity if low stock",
            "Feature product prominently (end caps, window display)",
            "Prepare staff FAQ on product benefits/usage",
            "Consider social media post capitalizing on trend"
        ],
        "timeline": "Execute within 24 hours (trends are fast!)",
        "owner": "Marketing + Buyers"
    }
}
```

---

## 📊 Daily Output Format

```json
{
  "date": "2025-11-15",
  "total_articles_scanned": 127,
  "events_detected": 8,
  "alerts_generated": 3,

  "alerts": [
    {
      "priority": 1,
      "urgency": "immediate",
      "event_type": "health_emergency",
      "title": "Norovirus Outbreak in Dublin Hospitals",
      "reason": "Health emergency in our area affecting OTC : GIT",
      "affected_locations": ["All locations"],
      "relevant_products": ["OTC : GIT"],
      "historical_context": "Peak demand is 2.1x baseline during outbreak",
      "playbook": "HEALTH_EMERGENCY_PLAYBOOK",
      "actions": [
        "Emergency stock check of relevant OTC medications",
        "Contact suppliers for emergency reorder if needed",
        "Brief pharmacy staff on expected customer questions"
      ],
      "deadline": "Execute immediately",
      "owner": "Head Pharmacist + Buyers"
    },
    {
      "priority": 2,
      "urgency": "within_week",
      "event_type": "major_event",
      "title": "Ed Sheeran Concert at 3Arena, June 20-22",
      "reason": "Large event (45,000 people) near 3 of our stores",
      "affected_locations": ["Baggot St", "Barrow St", "Mater Hospital"],
      "relevant_products": [
        "Travel toiletries",
        "Pain relief",
        "Energy drinks",
        "First aid"
      ],
      "historical_context": "Events increase foot traffic 15-30%",
      "playbook": "MAJOR_EVENT_PLAYBOOK",
      "actions": [
        "Check inventory of travel essentials at affected locations",
        "Increase staffing during event dates",
        "Prepare promotional bundles"
      ],
      "deadline": "Execute 5-7 days before event (by June 13)",
      "owner": "Operations Manager"
    },
    {
      "priority": 3,
      "urgency": "within_24h",
      "event_type": "viral_trend",
      "title": "Ozempic Searches Surge After Celebrity Interview",
      "reason": "Viral trend for product category we stock",
      "affected_locations": ["All locations"],
      "relevant_products": ["Weight management supplements"],
      "historical_context": "Current stock: 45 units across all locations",
      "playbook": "VIRAL_TREND_PLAYBOOK",
      "actions": [
        "Emergency stock check",
        "Order maximum available if low",
        "Prepare staff FAQ"
      ],
      "deadline": "Execute within 24 hours",
      "owner": "Marketing + Buyers"
    }
  ],

  "events_detected_but_not_alerted": [
    {
      "event_type": "weather_extreme",
      "title": "Rain forecasted for weekend",
      "reason_not_alerted": "Not extreme enough (severity: low)"
    }
  ]
}
```

---

## ✅ What LLM Does Well Here

1. ✅ **Event extraction** from unstructured text
2. ✅ **Classification** (is this a major event, health emergency, etc.?)
3. ✅ **Entity extraction** (dates, locations, products, numbers)
4. ✅ **Summarization** (key facts from article)
5. ✅ **Relevance scoring** (is this relevant to retail pharmacy?)

## ❌ What LLM Does NOT Do

1. ❌ **Predicting** sales numbers ("+40% increase")
2. ❌ **Forecasting** demand
3. ❌ **Recommending** specific quantities
4. ❌ **Making up** information not in the article
5. ❌ **Replacing** your data analysis

---

## 🎯 Summary: LLM as Smart Event Detector

```
News Article
    ↓
[LLM: Event Detector]
    ↓
Structured Event (facts only)
    ↓
[Rule Engine + Your Data: Context Matcher]
    ↓
YES/NO Alert + Playbook
    ↓
Human executes pre-defined playbook
```

**The Magic**: LLM reads unstructured news → extracts structured facts → your business logic decides what to do

**No Hallucination**: LLM can't make up numbers because it's not asked to predict anything, just extract and classify.

---

Want me to build a working prototype of this refined approach? It would be much simpler and more reliable than the forecasting version! 🎯

---

## 📊 Daily Features Engineering: Providing Context to the LLM & Rules Engine

The Context Matcher needs accurate, up-to-date business data to make good decisions. This section covers how to engineer **daily features** from sales data that serve as the foundation for alert evaluation.

### **Purpose of Daily Features**

Daily features answer key questions needed by the alert system:

1. **Baseline & Anomalies**: "Is today's sales normal or unusual?"
2. **Category Performance**: "How much do we usually sell in each product category?"
3. **Location Metrics**: "Which stores are doing well, which are struggling?"
4. **Historical Context**: "What happened last year in a similar situation?"
5. **Stock Health**: "Do we have buffer stock if demand spikes?"

### **Daily Feature Pipeline**

```
Raw Sales Data (hourly/daily transactions)
        ↓
[Aggregation Layer]
        ↓
Daily Sales Features
- Total revenue by day
- Sales by location
- Sales by category
- Category growth rates
        ↓
[Anomaly Detection]
        ↓
Baseline vs Observed
- Z-score deviations
- Compared to 7-day average
- Compared to same day last year
        ↓
[Context Cache]
        ↓
Ready for LLM/Rules Engine
```

### **Core Daily Features to Calculate**

#### **1. Daily Sales Aggregations**

```python
Daily Sales Features:
├── total_revenue: Sum of all sales
├── total_units_sold: Total quantity
├── avg_transaction_value: Average order value
├── transaction_count: Number of transactions
├── refund_percentage: % of sales refunded
└── profit_margin: Gross profit %

Category-Level:
├── {category}_revenue: Revenue per category
├── {category}_units: Units sold per category
├── {category}_growth_vs_yesterday: %change
├── {category}_growth_vs_last_year_same_day: % change
└── {category}_is_anomaly: Boolean flag

Location-Level:
├── {location}_revenue: Per-store revenue
├── {location}_traffic: Transaction count (proxy for foot traffic)
├── {location}_avg_ticket: Avg transaction value
├── {location}_performance_vs_avg: Above/below store network average
└── {location}_stock_urgency: Low stock risk score
```

#### **2. Anomaly Signals** (Critical for Alert Context)

These help the rules engine determine if an alert is timely:

```python
Anomaly Metrics:
├── is_high_volume_day: Sales > 90th percentile for day-of-week
├── is_low_volume_day: Sales < 10th percentile
├── category_surge: Any category > 2x normal
├── category_drought: Any category < 0.5x normal
├── unusual_refund_rate: Refunds > 5% (unusual high)
├── location_outperformance: Store > +20% network average
└── location_underperformance: Store < -20% network average
```

#### **3. Historical Baselines** (For Context Matching)

Stored for every significant dimension:

```python
Baselines (7-day, 30-day, YoY):
├── median_daily_revenue (7d, 30d, YoY)
├── p25_revenue (for "slow day" baseline)
├── p75_revenue (for "good day" baseline)
├── p95_revenue (for "exceptional" baseline)
├── category_peak_revenue (when does each category peak?)
├── category_seasonal_pattern (which months are strong?)
├── location_relative_strength (is location a strong performer?)
└── weekday_seasonality (how much does Mon differ from Fri?)
```

### **Data Engineering Implementation Approach**

#### **Option A: Batch Daily Aggregation (Recommended)**

**When**: Run once daily (e.g., 2am, after all previous day transactions complete)

**What it does**:
1. Load raw sales data from midnight yesterday to midnight today
2. Aggregate by day, category, location
3. Calculate anomalies vs baselines
4. Cache results in lightweight JSON/CSV

**Advantages**:
- ✅ Simple, reliable
- ✅ All data is final (no mid-day revisions)
- ✅ Easy to debug
- ✅ Fast (5-10 minutes for full aggregation)

**Output format**:
```python
{
  "date": "2025-11-15",
  "execution_time": "2025-11-16 02:15:30",

  "daily_totals": {
    "total_revenue": 45230.50,
    "total_units": 1250,
    "transaction_count": 890,
    "refund_percentage": 1.2,
    "avg_ticket": 50.82
  },

  "by_category": {
    "OTC : Cold & Flu": {
      "revenue": 3450.25,
      "units": 210,
      "growth_vs_yesterday": "+5.2%",
      "growth_vs_last_year": "+12.3%",
      "is_anomaly": false,
      "anomaly_score": 0.32
    },
    "Sunscreen & Sun Care": {
      "revenue": 1200.00,
      "units": 80,
      "growth_vs_yesterday": "+45.2%",
      "growth_vs_last_year": "+128.5%",
      "is_anomaly": true,
      "anomaly_score": 3.2,
      "likely_reasons": ["Heatwave forecasted", "Seasonal (summer)"]
    },
    # ... more categories
  },

  "by_location": {
    "Baggot St": {
      "revenue": 8450.00,
      "traffic": 145,
      "avg_ticket": 58.28,
      "vs_network_avg": "+8.5%",
      "stock_urgency": "low"
    },
    # ... more locations
  },

  "anomalies": {
    "high_volume_day": false,
    "low_volume_day": false,
    "category_surges": ["Sunscreen & Sun Care"],
    "category_droughts": [],
    "location_outliers": []
  },

  "historical_context": {
    "same_day_last_year": {
      "revenue": 38450.00,
      "growth_rate": "+17.6%"
    },
    "7_day_average": 41200.00,
    "30_day_average": 42100.00,
    "is_above_median": true
  }
}
```

#### **Option B: Real-Time Rolling Updates (Advanced)**

**When**: Update every 30 minutes with streaming data

**What it does**:
1. Maintains a rolling 24-hour window of recent sales
2. Continuously recalculates hot metrics (current hour spike?)
3. Feeds real-time anomaly detection

**Advantages**:
- ✅ Can detect intra-day spikes (e.g., viral product trend hits mid-morning)
- ✅ Enables real-time alerts

**Disadvantages**:
- ❌ More complex (streaming infrastructure needed)
- ❌ Higher compute costs
- ❌ More debugging challenges

**Recommendation**: Start with Option A (daily batch), upgrade to Option B if you need mid-day alert responsiveness.

### **Critical Features for Alert Context**

When the rules engine evaluates an alert, it needs:

**For Major Events**:
```python
# "Is this event going to impact us?"
needed_features = {
  "baseline_daily_traffic": baseline[affected_location]['traffic'],
  "typical_event_day_lift": 1.25,  # From historical event data
  "current_stock_buffer": stock[affected_location]['days_supply'],
  "staffing_availability": staffing_schedule[event_date]
}
```

**For Health Emergencies**:
```python
# "Do we have stock if there's a spike?"
needed_features = {
  "category_baseline_daily": category_stats['OTC : Cold & Flu']['daily_avg'],
  "category_peak_historical": category_stats['OTC : Cold & Flu']['peak_daily'],
  "current_stock_of_key_products": inventory_snapshot['OTC : Cold & Flu'],
  "supplier_lead_time": 3,  # days
  "stock_coverage_days": inventory / daily_avg  # How many days can we supply?
}
```

**For Viral Trends**:
```python
# "Can we capitalize on this?"
needed_features = {
  "trending_product_current_stock": inventory['trending_product'],
  "trending_product_daily_sales_normal": category_stats['weight_mgmt']['daily_avg'],
  "trending_product_peak_historical": category_stats['weight_mgmt']['peak_daily'],
  "supplier_lead_time": 5,  # days
  "product_in_all_locations": locations_stocking_product
}
```

### **Baseline Calculation Strategy**

**Three Baseline Types**:

1. **Short-term baseline (7-day rolling average)**
   - Use for: "Is today unusual?"
   - Advantage: Captures recent trends
   - Disadvantage: Can be affected by recent anomalies

2. **Medium-term baseline (30-day average)**
   - Use for: "Is this a sustained change or temporary?"
   - Advantage: Smooths out noise
   - Disadvantage: Slow to adapt

3. **Long-term baseline (same day last year)**
   - Use for: "What's the seasonal norm?"
   - Advantage: Accounts for seasonality
   - Disadvantage: Needs a full year of historical data

**Calculation at feature calculation time**:
```python
# For every date, calculate:
baselines[date] = {
  "7d_rolling_avg": sales[date-7:date].mean(),
  "30d_rolling_avg": sales[date-30:date].mean(),
  "last_year_same_day": sales[date-365],
  "weekday_typical": sales[where weekday=date.weekday, past 8 weeks].median()
}
```

### **Anomaly Detection Strategy**

**Z-Score Method** (recommended for simplicity):

```python
def calculate_anomaly_score(value, baseline_mean, baseline_std):
    """
    Z-score: How many standard deviations away from normal?

    z=0: Exactly normal
    z=2: 2 std above (unusual)
    z=3: 3 std above (very unusual)
    z>4: Extreme anomaly
    """
    z_score = (value - baseline_mean) / baseline_std

    if z_score > 3:
        return "critical_anomaly"
    elif z_score > 2:
        return "significant_anomaly"
    elif z_score > 1.5:
        return "minor_anomaly"
    else:
        return "normal"
```

**Multi-dimension anomalies**:
```python
# Flag if MULTIPLE dimensions are anomalous (reduces false positives)
daily_anomaly_score = {
  "revenue_z": calculate_z_score(daily_revenue, revenue_baseline),
  "category_anomalies": [c for c in categories if is_anomaly(c)],
  "location_anomalies": [l for l in locations if is_anomaly(l)],
  "refund_rate": daily_refunds / daily_revenue,

  # Only flag if 2+ dimensions are anomalous
  "is_true_anomaly": (
    len(category_anomalies) >= 2 OR
    len(location_anomalies) >= 2 OR
    (revenue_z > 2 AND refund_rate > 3%)
  )
}
```

### **Caching Strategy**

Store daily features in a lightweight cache (not database):

```python
# /data/cache/daily_features/
├── 2025-11-15.json          # Today's features
├── 2025-11-14.json          # Yesterday
├── 2025-11-13.json
└── baselines.json            # Pre-calculated baselines

# Load in Context Matcher:
context.daily_features = load_json("cache/daily_features/{today}.json")
context.baselines = load_json("cache/baselines.json")

# Available to rules engine:
context.daily_features['OTC : Cold & Flu']['revenue']  # →
 3450.25
context.baselines['OTC : Cold & Flu']['30d_avg']       # → 3200.00
```

### **Feature Freshness & Update Cadence**

```
Event Timeline:

05:00 - Previous day transactions finalize
    ↓
05:30 - Batch job: Calculate daily features
    ↓
06:00 - Features cached and ready
    ↓
06:05 - News Scout fetches morning news
    ↓
06:10 - Event Detector analyzes news
    ↓
06:15 - Context Matcher uses fresh features
    ↓
06:20 - Alerts generated with context
    ↓
06:30 - Human reviews alerts
```

**Key**: Daily features must be ready BEFORE morning news analysis.

### **Feature Store Responsibilities**

1. **Correctness**: Aggregations match raw data exactly
2. **Completeness**: Every category and location has features
3. **Timeliness**: Ready by 6am daily
4. **Auditability**: Can trace any feature back to raw data
5. **Catchup Logic**: If batch fails, can re-run for historical dates

### **Implementation Checklist**

- [ ] Daily batch aggregation script (Python pandas recommended)
- [ ] Anomaly detection thresholds tuned on historical data
- [ ] Baseline calculation for all categories and locations
- [ ] Caching layer (JSON files or lightweight DB like SQLite)
- [ ] Validation: Daily totals match raw data
- [ ] Monitoring: Alert if batch fails or takes >15min
- [ ] Historical backfill: Calculate features for past 12 months
- [ ] Integration: Context Matcher loads from cache
- [ ] Testing: Verify alert accuracy with features included vs excluded

---

## 🎯 Integration with Alert System

**Without Daily Features** (Bad):
```
Event: "Heatwave coming"
Context Matcher: "Should we alert?"
Problem: Doesn't know current sunscreen stock or demand baseline
```

**With Daily Features** (Good):
```
Event: "Heatwave coming next 3 days"
Daily Features: {
  "Sunscreen & Sun Care": {
    "current_stock": 240 units,
    "7d_avg_daily_sales": 12 units,
    "stock_coverage": 20 days,
    "yesterday_sales": 8 units (normal)
  }
}
Context Matcher Logic:
  - Heatwave expected in 3 days
  - Normal demand: 12 units/day
  - Likely peak demand (heatwave): 50 units/day (4x normal)
  - Need 150 units over 3 days
  - Have 240 units → ENOUGH STOCK
  - Decision: ALERT="YES" with recommendation "Stock is adequate, but monitor peak days"
```

This is the power of combining **domain knowledge (LLM detects events) + business context (your data via daily features) + logic (rules engine)**.

---

## 🎯 Alert-Specific Data Engineering Requirements

Based on your actual data structure (retail sales, inventory, by location), here's what needs to be engineered **for each alert type**:

### **1. MAJOR EVENTS Alert** (concerts, festivals, conferences)

**What the alert needs to know**:
- Is there an event near our locations with significant expected attendance?
- What's our typical foot traffic baseline for stores near the event?
- Can we handle the spike in customer volume?

**Data engineering required**:

```python
# Data Sources Available: Retail Sales Data
# Columns: Sale Date, Branch Name, Qty Sold, Turnover

features_for_major_events = {
    # Step 1: For each affected location, calculate traffic baseline
    "location_traffic_baseline": {
        "Baggot St": {
            "avg_transactions_per_day": 850,  # Count of Sale IDs per day
            "avg_transactions_per_hour": 35,   # Busiest vs slowest hours
            "peak_day_traffic": 1200,
            "slowest_day_traffic": 450,
        },
        # ... all locations
    },

    # Step 2: Identify high-velocity product categories for events
    "event_relevant_products": {
        "categories": [
            "OTC : Analgesics",          # Pain relief (headaches from crowds)
            "OTC : First Aid",            # Plasters, band-aids
            "OTC : Cold & Flu",           # Cough drops, tissues
            "Nutritional Supplements",    # Energy drinks, vitamins
            "Female Toiletries : Hygiene", # Travel sizes
        ],
        "baseline_daily_revenue": {},  # Revenue per category per day
        "peak_historical": {},         # Best day for each category
    },

    # Step 3: Check inventory buffer
    "inventory_status": {
        "Baggot St": {
            "OTC : Analgesics": {
                "current_stock_units": 245,
                "daily_avg_sales": 8,
                "days_of_supply": 30,
                "can_handle_4x_spike": True  # 32 units/day needed
            }
        }
    },

    # Step 4: Expected impact calculation
    "impact_estimate": {
        "event_attendance": 45000,
        "nearby_locations": ["Baggot St", "Barrow St"],
        "historical_event_foot_traffic_lift": 1.8,  # From past concert data
        "expected_additional_transactions": 280,  # 1.8x - 1.0x baseline
    }
}

# SQL queries to build these:
SELECT
    DATE(Sale Date) as day,
    COUNT(DISTINCT Sale ID) as transaction_count,
    COUNT(*) as line_items,
    SUM(Qty Sold) as total_units,
    SUM(Turnover) as daily_revenue
FROM retail_sales
WHERE Branch Name = 'Baggot St'
GROUP BY DATE(Sale Date)
ORDER BY day DESC

# Then calculate:
# - 7-day avg transactions (baseline)
# - Peak day (from full history)
# - Slowest day (from full history)
```

**Implementation checklist for Major Events**:
- [ ] Calculate transaction counts per store per day (from Sale Date & Sale ID)
- [ ] Calculate category revenue per store per day (GROUP BY Dept Fullname)
- [ ] Historical peaks for event-relevant categories (Analgesics, First Aid, Cold & Flu)
- [ ] Inventory check (Branch Stock Level for affected locations)
- [ ] Staffing availability (if you have staffing data)

---

### **2. HEALTH EMERGENCY Alert** (flu outbreak, norovirus, food poisoning)

**What the alert needs to know**:
- How much do we normally sell of the relevant medication category per day?
- What's our peak historical demand for this category (flu season)?
- Do we have enough stock to handle a 3-5x demand spike?
- How many days of supply do we have?

**Data engineering required**:

```python
features_for_health_emergency = {
    # Step 1: Establish baseline demand for relevant categories
    "category_demand_profiles": {
        "OTC : Cold & Flu": {
            "daily_avg_units": 42,           # Units from Qty Sold column
            "daily_avg_revenue": 285.50,
            "7d_avg_units": 44,
            "30d_avg_units": 40,

            # Peak demand (flu season or past outbreaks)
            "historical_peak_daily_units": 165,    # From Jan-Feb past years
            "historical_peak_daily_revenue": 1200,
            "peak_month": "February",

            # Emergency spike estimate
            "outbreak_estimated_peak": 180,  # 4-5x normal
        },

        "OTC : GIT": {  # GIT = Gastro-intestinal
            "daily_avg_units": 28,
            "daily_avg_revenue": 195.00,
            "historical_peak_daily_units": 95,
            "outbreak_estimated_peak": 120,
        },

        "OTC : Allergy": {  # For allergy-related health alerts
            "daily_avg_units": 18,
            "daily_avg_revenue": 125.00,
        }
    },

    # Step 2: Current inventory vs spike requirement
    "inventory_health": {
        "all_locations": {
            "OTC : Cold & Flu": {
                "total_current_stock": 450,      # Sum from all locations
                "normal_daily_consumption": 42,
                "days_of_supply_normal": 10.7,
                "outbreak_daily_consumption": 180,
                "days_of_supply_outbreak": 2.5,
                "ALERT_NEEDED": True,  # Less than 5 days at spike rate
            },
            "OTC : GIT": {
                "total_current_stock": 280,
                "days_of_supply_outbreak": 2.3,
                "ALERT_NEEDED": True,
            }
        },

        # Per-location breakdown
        "by_location": {
            "Baggot St": {
                "OTC : Cold & Flu": 125,
                "OTC : GIT": 85,
            },
            # ... all locations
        }
    },

    # Step 3: Supplier response capability
    "supplier_information": {
        # From OrderList in sales data - which suppliers provide these?
        "OTC : Cold & Flu": [
            {"supplier": "Kenvue (McNeil Healthcare)", "products": ["Actifed Tabs", "Ibuprofen"], "typical_lead_time_days": 3},
            {"supplier": "Pharmax", "products": ["Solpadeine", "Codeine"], "typical_lead_time_days": 2},
            # ... more suppliers
        ]
    },

    # Step 4: Time-to-stockout calculation
    "urgency_metrics": {
        "OTC : Cold & Flu": {
            "current_stock": 450,
            "at_spike_rate_stockout_hours": 180,  # (450 / 2.5 units per hour)
            "recommendation": "IMMEDIATE reorder - will stockout in ~7-8 days at outbreak peak"
        }
    }
}

# SQL queries needed:
SELECT
    Dept Fullname,
    DATE(Sale Date) as day,
    SUM(Qty Sold) as units_sold,
    SUM(Turnover) as revenue
FROM retail_sales
WHERE Dept Fullname IN ('OTC : Cold & Flu', 'OTC : GIT', 'OTC : Allergy')
GROUP BY Dept Fullname, DATE(Sale Date)
ORDER BY day DESC

# For peaks:
SELECT
    Dept Fullname,
    MONTH(Sale Date) as month,
    AVG(daily_units) as avg_units,
    MAX(daily_units) as peak_units
FROM (
    SELECT
        Dept Fullname,
        DATE(Sale Date) as day,
        SUM(Qty Sold) as daily_units
    FROM retail_sales
    GROUP BY Dept Fullname, DATE(Sale Date)
) daily_data
GROUP BY Dept Fullname, MONTH(Sale Date)

# For inventory:
SELECT
    Dept Fullname,
    SUM(Branch Stock Level) as total_stock
FROM retail_inventory
GROUP BY Dept Fullname
```

**Implementation checklist for Health Emergency**:
- [ ] Calculate daily sales (units & revenue) by category for past 24 months
- [ ] Identify seasonal peaks (Jan-Feb for flu, summer for food poisoning awareness)
- [ ] Calculate median daily, peak daily, and spike daily estimates
- [ ] Query current inventory by category (sum across all locations)
- [ ] Calculate days-of-supply at normal and spike rates
- [ ] Extract supplier information from OrderList (which supplier = which category?)
- [ ] Build supplier lead time database

---

### **3. WEATHER EXTREME Alert** (heatwave, cold snap, flooding)

**What the alert needs to know**:
- How much do weather-sensitive categories normally sell per day?
- What's the peak historical demand for this season?
- Can we stock up in advance?

**Data engineering required**:

```python
features_for_weather_extreme = {
    # Step 1: Weather-product mapping based on YOUR historical data
    "weather_category_mapping": {
        "heatwave": {
            "primary_categories": [
                "Skincare",                 # Sunscreen (SPF45 in your data)
                "OTC : Allergy",            # Hay fever from heat + pollen
                "Nutritional Supplements",  # Hydration products
            ],
            "secondary_categories": [
                "OTC : Analgesics",         # Headaches from heat
            ]
        },

        "cold_snap": {
            "primary_categories": [
                "OTC : Cold & Flu",         # Immunity boost
                "Vitamins",                 # Vitamin D deficiency
            ]
        },

        "flooding": {
            "primary_categories": [
                "OTC : First Aid",          # Cuts, wounds, hygiene
                "Female Toiletries : Hygiene",  # Hygiene in wet conditions
            ]
        }
    },

    # Step 2: Historical weather response from YOUR data
    "category_seasonal_patterns": {
        "Skincare": {
            "seasonal_baseline": {
                "Jan": {"daily_units": 85, "daily_revenue": 450},
                "Feb": {"daily_units": 90, "daily_revenue": 475},
                "Jun": {"daily_units": 210, "daily_revenue": 1100},  # Summer peak
                "Jul": {"daily_units": 245, "daily_revenue": 1300},  # Highest
                "Aug": {"daily_units": 220, "daily_revenue": 1150},
            },

            "heatwave_uplift": {
                # Look at Jul 2024 (hot month) vs normal June baseline
                "expected_spike_factor": 1.8,  # 1.8x normal summer baseline
                "peak_observed_daily_units": 440,  # Historical max in heatwave month
                "peak_observed_daily_revenue": 2300,
            },

            "inventory_consideration": {
                "current_stock": 520,  # From inventory snapshot
                "normal_summer_daily_consumption": 210,
                "heatwave_daily_consumption": 378,
                "days_of_supply_normal": 2.5,
                "days_of_supply_heatwave": 1.4,
                "recommendation": "LOW - reorder if heatwave expected"
            }
        },

        "OTC : Cold & Flu": {
            "seasonal_baseline": {
                "Jan": {"daily_units": 95, "daily_revenue": 650},
                "Feb": {"daily_units": 105, "daily_revenue": 720},
                "Jun": {"daily_units": 18, "daily_revenue": 120},
                "Jul": {"daily_units": 15, "daily_revenue": 95},
            },
            "cold_snap_uplift": {
                "expected_spike_factor": 2.2,
                "peak_observed_daily_units": 210,
            }
        }
    },

    # Step 3: By-location impact
    "location_weather_vulnerability": {
        "Baggot St": {
            "heatwave_impact": "high",      # Central Dublin, busy area
            "cold_snap_impact": "medium",
            "flooding_risk": "low"           # Not flood-prone area
        },
        "Churchtown": {
            "heatwave_impact": "medium",
            "cold_snap_impact": "high",      # Suburban, colder
            "flooding_risk": "high"          # Known flooding area
        }
        # ... all locations
    }
}

# SQL queries needed:

# Calculate daily sales by month-year and category
SELECT
    DATE_TRUNC('month', Sale Date) as month,
    Dept Fullname,
    SUM(Qty Sold) as units,
    SUM(Turnover) as revenue,
    COUNT(DISTINCT DATE(Sale Date)) as selling_days,
    SUM(Qty Sold) / COUNT(DISTINCT DATE(Sale Date)) as daily_avg_units
FROM retail_sales
WHERE Dept Fullname IN ('Skincare', 'OTC : Cold & Flu', 'OTC : Allergy', 'Vitamins')
GROUP BY month, Dept Fullname
ORDER BY month DESC

# Identify extreme days within peak seasons
SELECT
    DATE(Sale Date) as day,
    Dept Fullname,
    SUM(Qty Sold) as daily_units,
    SUM(Turnover) as daily_revenue
FROM retail_sales
WHERE
    Dept Fullname = 'Skincare'
    AND MONTH(Sale Date) IN (6,7,8)  -- Summer months
    AND YEAR(Sale Date) >= 2023
GROUP BY DATE(Sale Date), Dept Fullname
ORDER BY daily_units DESC
```

**Implementation checklist for Weather Extreme**:
- [ ] Build month-by-month category sales baseline (past 24 months)
- [ ] Identify seasonal peaks vs valleys for each weather-sensitive category
- [ ] Calculate spike factors (how much above baseline during that season?)
- [ ] Map which locations are vulnerable to which weather conditions
- [ ] Current inventory for weather-sensitive categories
- [ ] Supplier lead times for high-volume reorders

---

### **4. COMPETITOR ACTION Alert** (new store, promotion, closing)

**What the alert needs to know**:
- Which of our locations are near the competitor action?
- What's our market performance in that area?
- How many customers/sales could be at risk?

**Data engineering required**:

```python
features_for_competitor_action = {
    # Step 1: Location market performance baseline
    "location_performance": {
        "Baggot St": {
            "daily_transactions": 845,
            "daily_revenue": 8200,
            "revenue_rank": 1,  # Best performing
            "market_share_estimate": "18% of total network",
            "customer_traffic_variability": 0.15,  # Stable location
        },
        "Churchtown": {
            "daily_transactions": 580,
            "daily_revenue": 5400,
            "revenue_rank": 3,
            "market_share_estimate": "12% of total network",
            "customer_traffic_variability": 0.22,  # More volatile
        }
        # ... all locations
    },

    # Step 2: Geographic vulnerability
    "location_coordinates": {
        "Baggot St": {"area": "Dublin 4", "competitor_density": "high"},
        "Churchtown": {"area": "Dublin 14", "competitor_density": "medium"},
        # ... all locations with estimated coordinates
    },

    # Step 3: Competitive product categories
    "competitive_categories": {
        # Which categories are most price-sensitive?
        # Which have thinnest margins?
        "OTC : Analgesics": {
            "margin": 0.35,         # ~35% margin
            "competitor_risk": "HIGH",
            "our_revenue_share": 0.15
        },
        "Vitamins": {
            "margin": 0.40,
            "competitor_risk": "HIGH",
            "our_revenue_share": 0.12
        },
        "Skincare": {
            "margin": 0.45,
            "competitor_risk": "MEDIUM",
            "our_revenue_share": 0.08
        }
    },

    # Step 4: Historical response to competition
    "historical_competitive_response": {
        "when_competitor_opened_store_X": {
            "nearby_location": "Barrow St",
            "impact_on_baggot_st_traffic": -8.5,  # % decline
            "impact_on_barrow_st_traffic": -15.2,
            "recovery_time_days": 45,
            "effective_countermeasure": "10% loyalty program bonus"
        }
    },

    # Step 5: Recommendation data
    "competitive_response_options": {
        "immediate_actions": [
            "Verify competitor's product range vs ours",
            "Check their pricing on key categories",
            "Sample customer feedback (mystery shop)"
        ],
        "pricing_comparison": {
            "need_to_collect": [
                "Competitor OTC : Analgesics prices",
                "Competitor Vitamin prices",
                "Our current prices vs last month"
            ]
        }
    }
}

# SQL queries needed:

# Location performance baseline
SELECT
    Branch Name,
    COUNT(DISTINCT DATE(Sale Date)) as operating_days,
    COUNT(DISTINCT Sale ID) as total_transactions,
    SUM(Turnover) as total_revenue,
    ROUND(COUNT(DISTINCT Sale ID) / COUNT(DISTINCT DATE(Sale Date)), 0) as avg_daily_transactions,
    ROUND(SUM(Turnover) / COUNT(DISTINCT DATE(Sale Date)), 2) as avg_daily_revenue
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY Branch Name
ORDER BY total_revenue DESC

# Category performance by location
SELECT
    Branch Name,
    Dept Fullname,
    SUM(Turnover) as total_revenue,
    SUM(Qty Sold) as total_units,
    AVG(Turnover / NULLIF(Qty Sold, 0)) as avg_price_per_unit
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY Branch Name, Dept Fullname
ORDER BY Branch Name, total_revenue DESC

# Trend for specific location (to detect competitor impact)
SELECT
    DATE(Sale Date) as day,
    Branch Name,
    COUNT(DISTINCT Sale ID) as daily_transactions,
    SUM(Turnover) as daily_revenue
FROM retail_sales
WHERE Branch Name = 'Baggot St'
GROUP BY DATE(Sale Date), Branch Name
ORDER BY day DESC
```

**Implementation checklist for Competitor Action**:
- [ ] Calculate revenue and transaction baseline per location (past 12 months)
- [ ] Rank locations by performance (top vs bottom performers)
- [ ] Identify margin-sensitive categories (Analgesics vs Skincare)
- [ ] Build competitor response playbook database
- [ ] Track location vulnerability scores (high-risk areas)
- [ ] Historical competitor impact measurements (if available)

---

### **5. SUPPLY DISRUPTION Alert** (supplier bankruptcy, strikes, port issues)

**What the alert needs to know**:
- Which suppliers are critical to our operations?
- What products rely on these suppliers?
- How much stock do we have of at-risk products?
- How long can we supply customers if supplier fails?

**Data engineering required**:

```python
features_for_supply_disruption = {
    # Step 1: Supplier importance ranking
    "supplier_criticality": {
        # From OrderList in your sales data
        "Kenvue (McNeil Healthcare)": {
            "revenue_dependency": 0.22,  # 22% of our revenue
            "product_count": 48,
            "categories": ["OTC : Cold & Flu", "OTC : Analgesics"],
            "monthly_spend_estimate": 12000,
            "criticality_rank": "CRITICAL"
        },

        "Pharmax": {
            "revenue_dependency": 0.15,
            "product_count": 32,
            "categories": ["OTC : Analgesics", "OTC : GIT"],
            "monthly_spend_estimate": 8000,
            "criticality_rank": "CRITICAL"
        },

        "Wholefoods Wholesale": {
            "revenue_dependency": 0.12,
            "product_count": 28,
            "categories": ["Vitamins", "Nutritional Supplements"],
            "monthly_spend_estimate": 6500,
            "criticality_rank": "HIGH"
        },

        "Haleon (GSK)": {
            "revenue_dependency": 0.09,
            "product_count": 22,
            "categories": ["OTC : Analgesics", "Skincare"],
            "monthly_spend_estimate": 5000,
            "criticality_rank": "HIGH"
        }
    },

    # Step 2: Supplier product vulnerability
    "supplier_product_dependency": {
        "OTC : Cold & Flu": {
            "suppliers": [
                {"name": "Kenvue (McNeil Healthcare)", "% of category": 0.35},
                {"name": "Pharmax", "% of category": 0.25},
                {"name": "Reckitt Benckiser Group", "% of category": 0.20},
            ],
            "if_kenvue_fails": {
                "impact": "Can cover with other suppliers, but limited variety",
                "stock_buffer_days": 8
            }
        }
    },

    # Step 3: Stock resilience
    "supply_chain_resilience": {
        "by_supplier": {
            "Kenvue (McNeil Healthcare)": {
                "critical_products": [
                    {
                        "product": "Actifed Tabs 12s",
                        "current_stock": 85,
                        "daily_sales": 3.2,
                        "days_of_supply": 26.5,
                        "alternative_suppliers": ["Pharmax"]
                    },
                    {
                        "product": "Solpadeine Soluble 24s",
                        "current_stock": 120,
                        "daily_sales": 4.8,
                        "days_of_supply": 25,
                        "alternative_suppliers": ["Pharmax", "Haleon"]
                    }
                ],
                "total_days_of_supply_across_category": 20,
                "can_weather_2week_shortage": False,
                "action_required": "Yes - identify alternative suppliers"
            }
        }
    },

    # Step 4: Alternative supplier availability
    "supply_alternatives": {
        "for_kenvue_products": [
            {
                "alternative": "Pharmax",
                "overlap_products": 8,
                "lead_time_to_supply": 3,
                "cost_delta": "+8%"  # Likely more expensive
            },
            {
                "alternative": "Haleon (GSK)",
                "overlap_products": 5,
                "lead_time_to_supply": 4,
                "cost_delta": "+12%"
            }
        ]
    },

    # Step 5: Risk timeline
    "disruption_scenarios": {
        "port_strike_3_days": {
            "affected_suppliers": ["Kenvue", "Haleon"],  # If coming from EU
            "affected_categories": ["OTC : Analgesics", "OTC : Cold & Flu"],
            "stockout_risk": "LOW" if days_of_supply > 3 else "HIGH",
            "action": "Monitor, can absorb with current stock"
        },
        "supplier_bankruptcy_immediate": {
            "affected_suppliers": ["Kenvue"],
            "recovery_time": "5-10 days to activate alternatives",
            "stockout_risk": "HIGH",
            "action": "IMMEDIATELY contact alternatives"
        }
    }
}

# SQL queries needed:

# Supplier revenue dependency
SELECT
    OrderList as supplier,
    COUNT(DISTINCT Product) as product_count,
    COUNT(DISTINCT Dept Fullname) as category_count,
    SUM(Turnover) as total_revenue,
    ROUND(SUM(Turnover) / (SELECT SUM(Turnover) FROM retail_sales WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)) * 100, 1) as revenue_percentage
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY OrderList
ORDER BY total_revenue DESC

# Supplier category breakdown
SELECT
    OrderList as supplier,
    Dept Fullname as category,
    COUNT(DISTINCT Product) as product_count,
    SUM(Qty Sold) as units,
    SUM(Turnover) as revenue
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 12 MONTH)
GROUP BY OrderList, Dept Fullname
ORDER BY OrderList, revenue DESC

# Days of supply for critical products
SELECT
    Product,
    OrderList as supplier,
    Dept Fullname,
    inv.Branch Stock Level as current_stock,
    ROUND(SUM(sales.Qty Sold) / COUNT(DISTINCT DATE(sales.Sale Date)), 1) as daily_sales,
    ROUND(inv.Branch Stock Level / (SUM(sales.Qty Sold) / COUNT(DISTINCT DATE(sales.Sale Date))), 1) as days_of_supply
FROM retail_sales sales
JOIN retail_inventory inv ON sales.Product = inv.Product
WHERE sales.Sale Date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
GROUP BY Product, OrderList, Dept Fullname
ORDER BY days_of_supply ASC
```

**Implementation checklist for Supply Disruption**:
- [ ] Build supplier-to-product mapping from OrderList
- [ ] Calculate supplier revenue dependency (% of total business)
- [ ] Identify category-to-supplier relationships
- [ ] Calculate days-of-supply for each critical product
- [ ] Build supplier alternative database
- [ ] Document lead times and cost deltas for alternatives
- [ ] Create supplier vulnerability score (criticality × low_stock × single_source)

---

### **6. VIRAL TREND Alert** (celebrity mention, TikTok trend)

**What the alert needs to know**:
- Do we stock the trending product?
- How much stock do we have right now?
- What's the normal daily sales rate?
- Can we capture the spike or will we stockout?

**Data engineering required**:

```python
features_for_viral_trend = {
    # Step 1: Product inventory snapshot
    "product_coverage": {
        "by_location": {
            "all_locations": {
                "total_products": 3847,
                "actively_stocked": 3250,  # Not delisted
                "in_all_8_locations": 420,  # Available everywhere
                "single_location_only": 890
            }
        }
    },

    # Step 2: If product is trendy (e.g., "Ozempic" = weight loss)
    "trending_product_example": {
        "trend": "Ozempic celebrity mention",
        "our_equivalent_categories": [
            "Nutritional Supplements : Diet",
            "Weight management supplements",
            "Vitamins (specifically B-complex, Vitamin D for metabolism)"
        ],

        "product_examples_in_inventory": [
            {
                "product": "Linwoods Flax Seed 425G",
                "category": "Nutritional Supplements : Diet",
                "current_stock": {
                    "Baggot St": 8,
                    "Barrow St": 12,
                    "Churchtown": 0,
                    "Castletymon": 5,
                    # ...all locations
                    "total": 45
                },
                "daily_sales_normal": 0.8,
                "days_of_supply": 56,
                "peak_capacity": 2.5,
                "days_of_supply_at_peak": 18,
                "can_capitalize": True
            },
            {
                "product": "Some Weight Loss Supplement",
                "current_stock": 280,
                "daily_sales_normal": 2.1,
                "peak_multiplier": 3.8,  # Expected 3.8x normal
                "days_of_supply_at_peak": 3.5,
                "risk": "HIGH - will stockout in 3-4 days"
            }
        ]
    },

    # Step 3: Viral trend capture capability
    "capture_readiness": {
        "weight_loss_supplements": {
            "current_trend_status": "VIRAL",
            "estimated_peak_duration_days": 7,
            "estimated_volume_multiplier": 4.5,
            "current_stock_adequacy": "INSUFFICIENT",
            "reorder_urgency": "IMMEDIATE - 24 hours",
            "supplier_lead_time": 5,
            "stockout_risk": "HIGH",
            "recommendation": "Order max available from all suppliers TODAY"
        }
    },

    # Step 4: Sales impact projection
    "sales_opportunity": {
        "if_fully_stocked": {
            "weight_loss_supplements": {
                "normal_weekly_revenue": 145,
                "viral_week_revenue_estimate": 655,  # 4.5x
                "opportunity_value": 510
            }
        },
        "if_stockout": {
            "lost_revenue": 510,
            "lost_future_customers": "moderate" # Some will shop elsewhere
        }
    }
}

# SQL queries needed:

# Current product inventory
SELECT
    Product,
    Dept Fullname,
    COUNT(*) as location_count,  # How many locations stock it
    SUM(CAST(Branch Stock Level AS FLOAT)) as total_stock,
    MIN(CAST(Branch Stock Level AS FLOAT)) as min_stock_location,
    MAX(CAST(Branch Stock Level AS FLOAT)) as max_stock_location
FROM retail_inventory
WHERE Product LIKE '%weight%' OR Dept Fullname LIKE '%Diet%'
GROUP BY Product, Dept Fullname
ORDER BY total_stock DESC

# Daily sales rate (last 30 days)
SELECT
    Product,
    Dept Fullname,
    COUNT(DISTINCT DATE(Sale Date)) as selling_days,
    SUM(Qty Sold) as total_units,
    ROUND(SUM(Qty Sold) / COUNT(DISTINCT DATE(Sale Date)), 2) as daily_avg_units,
    ROUND(SUM(Turnover) / COUNT(DISTINCT DATE(Sale Date)), 2) as daily_avg_revenue,
    MAX(Qty Sold) as peak_day_units
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
    AND (Product LIKE '%weight%' OR Dept Fullname LIKE '%Diet%')
GROUP BY Product, Dept Fullname
ORDER BY daily_avg_units DESC

# Peak historical performance
SELECT
    Product,
    DATE(Sale Date) as day,
    SUM(Qty Sold) as daily_units,
    SUM(Turnover) as daily_revenue,
    YEAR(Sale Date) as year,
    MONTH(Sale Date) as month
FROM retail_sales
WHERE Dept Fullname = 'Nutritional Supplements : Diet'
GROUP BY Product, DATE(Sale Date)
ORDER BY daily_units DESC
LIMIT 100  -- Top 100 sales days for this category
```

**Implementation checklist for Viral Trend**:
- [ ] Build product-to-inventory mapping (which locations stock what)
- [ ] Calculate daily sales rate for each trending-prone category
- [ ] Identify historical peaks for each category (what's the max we've sold?)
- [ ] Current inventory levels per location per product
- [ ] Supplier availability and lead times for quick reorders
- [ ] Build "reorder trigger" logic (if viral → auto-flag for emergency order)

---

### **7. REGULATORY CHANGE Alert** (drug reclassifications, tax changes)

**What the alert needs to know**:
- Do we stock the affected products?
- How much revenue do they generate?
- What operational changes are needed?

**Data engineering required**:

```python
features_for_regulatory_change = {
    # Step 1: Product classification mapping
    "product_categories": {
        # Build a mapping of products to their regulatory classification
        "prescription_to_OTC_risk": {
            # Which of our products might move from Rx → OTC?
            "products_potentially_affected": [
                {
                    "product": "Pantoprazole",  # Example
                    "current_classification": "OTC",
                    "current_revenue": 450,
                    "current_daily_sales": 3.2,
                    "if_reclassified_to_OTC": {
                        "impact": "POSITIVE - more customers can buy",
                        "expected_volume_lift": 2.5,
                        "expected_new_daily_sales": 8.0
                    }
                }
            ]
        },

        "tax_affected_products": {
            # Which categories would be affected by VAT changes?
            "vitamins": {
                "current_vat_rate": 0,  # Typically zero-rated in Ireland
                "revenue_if_vat_added": 850000,  # Annual from our data
                "customer_price_sensitivity": "HIGH"
            },
            "skincare": {
                "current_vat_rate": 23,
                "revenue": 120000,
                "customer_price_sensitivity": "MEDIUM"
            }
        }
    },

    # Step 2: Affected product list
    "regulatory_impact_by_product": {
        "from_sales_data": {
            # Examples from your actual products
            "OTC : Analgesics": {
                "revenue_last_month": 3450,
                "units_last_month": 280,
                "affected_by_regulation": False
            },
            "Vitamins": {
                "revenue_last_month": 5200,
                "units_last_month": 420,
                "affected_by_regulation": "MAYBE",
                "reason": "If VAT changes"
            }
        }
    },

    # Step 3: Operational impact
    "operational_requirements": {
        "staff_training": {
            "needed": True,
            "affected_roles": ["Pharmacists", "Counter staff"],
            "topics": ["New labeling requirements", "New counseling points"]
        },
        "inventory_adjustment": {
            "needed": False,  # Usually just relabeling
        },
        "system_changes": {
            "pos_system": "May need category relabeling",
            "pricing": "May change if VAT affected",
            "compliance_documentation": "Required"
        }
    },

    # Step 4: Timeline criticality
    "effective_date_impact": {
        "days_until_effective": 30,
        "compliance_deadline": "2025-12-15",
        "urgency": "within_week"  # As effective date approaches
    }
}

# SQL queries needed:

# All products by category (regulatory classification)
SELECT
    Dept Fullname,
    GROUP_FULLNAME,
    COUNT(DISTINCT Product) as product_count,
    SUM(Turnover) as total_revenue,
    COUNT(DISTINCT DATE(Sale Date)) as selling_days
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
GROUP BY Dept Fullname, Group Fullname
ORDER BY total_revenue DESC

# Products that might be affected (search by keyword)
SELECT
    Product,
    Dept Fullname,
    OrderList as supplier,
    SUM(Qty Sold) as units_last_30d,
    SUM(Turnover) as revenue_last_30d
FROM retail_sales
WHERE Sale Date >= DATE_SUB(NOW(), INTERVAL 30 DAYS)
    AND Product LIKE '%[affected_product_keyword]%'
GROUP BY Product, Dept Fullname, OrderList
ORDER BY revenue_last_30d DESC
```

**Implementation checklist for Regulatory Change**:
- [ ] Build product-to-regulation mapping (which products affected by which rules?)
- [ ] Calculate revenue impact per affected product
- [ ] Identify operational changes needed (staff training, labeling, pricing)
- [ ] Extract effective dates from regulation changes
- [ ] Build compliance checklist per product category
- [ ] Timeline for implementation (how long to staff training, system changes?)

---

## 📋 Data Engineering Priority & Execution Order

**Recommended implementation sequence**:

1. **Week 1**: Daily aggregation + anomalies (needed by ALL alerts)
   - Daily sales by category, location, day
   - Historical baselines (7/30/365-day)
   - Z-score anomaly detection

2. **Week 2**: Health Emergency + Major Events (highest impact potential)
   - Category demand profiles
   - Inventory by location
   - Supplier lead times

3. **Week 3**: Competitor + Supply Disruption
   - Location performance ranking
   - Supplier criticality scores
   - Product-to-supplier mapping

4. **Week 4**: Viral Trends + Weather + Regulatory
   - Product availability by location
   - Category seasonal patterns
   - Regulatory product mappings

---

This is the **data foundation** your alert system needs to make smart, context-aware decisions!
