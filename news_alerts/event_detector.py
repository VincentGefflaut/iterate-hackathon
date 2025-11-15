"""
Event Detector Agent using Claude API with structured outputs.

Detects black swan events from news articles and extracts structured data.
Based on NEWS_ALERTS_REFOCUSED.md architecture.
"""

import anthropic
import os
import time
from typing import Optional
from datetime import datetime
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (two levels up from this file)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, will fall back to system env vars
    pass

from .models import NewsArticle, DetectedEvent, EventDetectionResult


class EventDetectorAgent:
    """
    Detects black swan events from news articles

    ONLY extracts facts, NO predictions
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize event detector

        Args:
            api_key: Anthropic API key (can also set ANTHROPIC_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def detect_event(self, article: NewsArticle, event_types: list = None) -> EventDetectionResult:
        """
        Analyze a news article and detect events

        Args:
            article: NewsArticle to analyze
            event_types: Optional list of event types to focus on (default: all)

        Returns:
            EventDetectionResult with detected event or None
        """
        start_time = time.time()

        try:
            event = self._analyze_article(article, event_types)
            processing_time = (time.time() - start_time) * 1000

            return EventDetectionResult(
                article=article,
                detected_event=event,
                detection_time=datetime.now().isoformat(),
                processing_time_ms=processing_time,
                error=None
            )
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return EventDetectionResult(
                article=article,
                detected_event=None,
                detection_time=datetime.now().isoformat(),
                processing_time_ms=processing_time,
                error=str(e)
            )

    def _analyze_article(
        self,
        article: NewsArticle,
        event_types: Optional[list] = None
    ) -> Optional[DetectedEvent]:
        """
        Analyze single article for events using Claude

        Args:
            article: NewsArticle to analyze
            event_types: Optional list of event types to focus on

        Returns:
            DetectedEvent if found, None otherwise
        """
        # Build prompt based on event types
        if event_types is None or len(event_types) == 0:
            event_types = ["major_event", "health_emergency", "weather_extreme",
                          "economic_shock", "competitor_action", "regulatory_change",
                          "supply_disruption", "viral_trend"]

        prompt = self._build_detection_prompt(article, event_types)

        # Call Claude with structured output
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1500,
            temperature=0.2,  # Low temp for factual extraction
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "extract_event",
                "description": "Extract structured event from article if it matches criteria",
                "input_schema": DetectedEvent.model_json_schema()
            }]
        )

        # Parse structured output
        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            try:
                event = DetectedEvent(**tool_use.input)
                # Only return if not "other" type
                if event.event_type != "other":
                    return event
            except Exception as e:
                print(f"Error parsing event: {e}")
                return None

        return None

    def _build_detection_prompt(self, article: NewsArticle, event_types: list) -> str:
        """Build detection prompt based on event types"""

        # Build event type descriptions
        event_descriptions = self._get_event_descriptions(event_types)

        prompt = f"""You are an event detection system for a retail pharmacy chain in Dublin, Ireland.

Your ONLY job is to detect external events from news that could affect a retail pharmacy business.

NEWS ARTICLE:
Title: {article.title}
Content: {article.description or article.content or 'No content available'}
Published: {article.published_at}
Source: {article.source}
URL: {article.url}

YOUR TASK:
Determine if this article describes a BLACK SWAN EVENT in one of these categories:

{event_descriptions}

CRITICAL RULES:
- If the article doesn't describe any of these event types, return NULL (do not use the tool)
- Extract ONLY facts from the article - NO predictions, NO guessing
- Do NOT predict sales impact or quantities
- Do NOT add information not in the article
- Focus on events in Ireland/Dublin (but include major global events if severe)

Example GOOD extraction:
{{
  "event_type": "major_event",
  "title": "Taylor Swift Concert Announced",
  "description": "Taylor Swift will perform three nights at 3Arena in Dublin",
  "severity": "medium",
  "event_date": "2025-06-15 to 2025-06-17",
  "location": "3Arena, Dublin",
  "expected_attendance": 45000,
  "key_facts": [
    "Three-night concert",
    "June 15-17, 2025",
    "Tickets selling out fast",
    "Expected 15,000 per night"
  ],
  "potential_relevance": "Major influx of visitors to Dublin area. Stores near 3Arena may see increased foot traffic.",
  "confidence": "high",
  "urgency": "within_month",
  "source_url": "{article.url}",
  "published_at": "{article.published_at}"
}}

Example BAD extraction (DON'T DO THIS):
{{
  "event_type": "major_event",
  "title": "Concert announced",
  "predicted_sales_increase": "+35%",  ← NO! Don't predict
  "recommended_stock": "500 units"     ← NO! Don't recommend
}}

Analyze this article and extract the event if it matches our categories.
If it doesn't match, DO NOT use the tool - just respond with text explaining why.
"""
        return prompt

    def _get_event_descriptions(self, event_types: list) -> str:
        """Get descriptions for specified event types"""

        descriptions = {
            "major_event": """1. MAJOR EVENT: Concert, festival, conference, sporting event bringing crowds to Dublin
   - Extract: date, location, expected attendance
   - Example: "Taylor Swift concert at 3Arena, June 15"
""",
            "health_emergency": """2. HEALTH EMERGENCY: Outbreak, disease alert, food poisoning, air quality warning
   - Extract: what, where, severity
   - Example: "Norovirus outbreak in Dublin hospitals"
""",
            "weather_extreme": """3. WEATHER EXTREME: Heatwave, storm, flooding (EXTREME only, not normal weather)
   - Extract: what, when, affected areas
   - Example: "Met Éireann red alert: Storm approaching"
""",
            "economic_shock": """4. ECONOMIC SHOCK: Currency crash, major layoffs, bank failure
   - Extract: what happened, scale
   - Example: "Major tech company lays off 5,000 in Dublin"
""",
            "competitor_action": """5. COMPETITOR ACTION: New pharmacy opening, major competitor promo, competitor closing
   - Extract: competitor name, location, what they're doing
   - Example: "Boots opening mega-store in Dundrum"
""",
            "regulatory_change": """6. REGULATORY CHANGE: Drug reclassifications, health regulations, tax changes
   - Extract: what changed, when effective, what products
   - Example: "Pantoprazole moves from prescription to OTC"
""",
            "supply_disruption": """7. SUPPLY DISRUPTION: Supplier bankruptcy, strikes, transportation issues, recalls
   - Extract: what's disrupted, which suppliers/products
   - Example: "Port strike delays shipments from EU"
""",
            "viral_trend": """8. VIRAL TREND: Celebrity health scare, TikTok product going viral, media health scare
   - Extract: what product, why trending
   - Example: "Ozempic searches surge after celebrity mention"
"""
        }

        # Build descriptions for requested event types
        result = []
        for i, event_type in enumerate(event_types, 1):
            if event_type in descriptions:
                # Replace number prefix
                desc = descriptions[event_type].replace(f"{list(descriptions.keys()).index(event_type) + 1}.", f"{i}.")
                result.append(desc)

        return "\n".join(result)

    def detect_health_emergency(self, article: NewsArticle) -> EventDetectionResult:
        """
        Specialized detector for health emergencies

        Focuses only on health-related events for better accuracy
        """
        return self.detect_event(article, event_types=["health_emergency"])

    def detect_major_event(self, article: NewsArticle) -> EventDetectionResult:
        """
        Specialized detector for major events

        Focuses only on concerts, festivals, conferences, sporting events
        """
        return self.detect_event(article, event_types=["major_event"])


# Example usage
if __name__ == "__main__":
    # Example article
    test_article = NewsArticle(
        title="Norovirus Outbreak Reported in Dublin Hospitals",
        description="Health officials have confirmed a norovirus outbreak affecting multiple hospitals in Dublin. Over 50 cases reported in the past week.",
        content="Dublin health authorities are investigating a norovirus outbreak that has affected several hospitals across the city...",
        url="https://example.com/news/norovirus",
        published_at="2024-11-15T10:00:00Z",
        source="Irish Times"
    )

    # Initialize detector
    detector = EventDetectorAgent()

    # Detect event
    result = detector.detect_health_emergency(test_article)

    if result.detected_event:
        print(f"Event detected: {result.detected_event.event_type}")
        print(f"Title: {result.detected_event.title}")
        print(f"Severity: {result.detected_event.severity}")
        print(f"Confidence: {result.detected_event.confidence}")
        print(f"Processing time: {result.processing_time_ms:.0f}ms")
    else:
        print("No event detected")
        if result.error:
            print(f"Error: {result.error}")
