"""
Product-aware event detector that focuses on product-related alerts.

Detects events that specifically impact products in the top.csv data.
"""

from typing import List, Optional, Set
from datetime import datetime
import time

from .event_detector import EventDetectorAgent
from .models import NewsArticle, DetectedEvent, EventDetectionResult
from .top_products_loader import TopProductsLoader


class ProductEventDetector(EventDetectorAgent):
    """
    Extended event detector that focuses on product-related events

    Detects events that could impact specific products:
    - Shortages/supply disruptions
    - Health trends affecting product demand
    - Regulatory changes for products
    - Competitor actions
    - Viral trends
    """

    def __init__(self, api_key: Optional[str] = None, csv_path: Optional[str] = None):
        """
        Initialize product event detector

        Args:
            api_key: Anthropic API key
            csv_path: Path to top.csv (optional)
        """
        super().__init__(api_key)
        self.products_loader = TopProductsLoader(csv_path) if csv_path else None
        self.tracked_products = self._get_tracked_products()

    def _get_tracked_products(self) -> Set[str]:
        """Get set of products we're tracking"""
        if self.products_loader:
            return self.products_loader.get_unique_products()
        else:
            # Default products from top.csv
            return {
                "Vitamins & Supplements",
                "Cleanser",
                "Serum"
            }

    def detect_product_event(
        self,
        article: NewsArticle,
        focus_products: List[str] = None
    ) -> EventDetectionResult:
        """
        Detect product-related events with enhanced focus on products

        Args:
            article: NewsArticle to analyze
            focus_products: Optional list of specific products to focus on

        Returns:
            EventDetectionResult with product-specific analysis
        """
        start_time = time.time()

        try:
            event = self._analyze_product_article(article, focus_products)
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

    def _analyze_product_article(
        self,
        article: NewsArticle,
        focus_products: Optional[List[str]] = None
    ) -> Optional[DetectedEvent]:
        """
        Analyze article for product-related events

        Args:
            article: NewsArticle to analyze
            focus_products: Optional list of products to focus on

        Returns:
            DetectedEvent if found, None otherwise
        """
        products_list = focus_products or list(self.tracked_products)
        products_str = ", ".join(products_list)

        prompt = f"""You are a product monitoring system for a retail pharmacy chain in Ireland.

Your ONLY job is to detect events that could impact demand or supply for these products:
{products_str}

NEWS ARTICLE:
Title: {article.title}
Content: {article.description or article.content or 'No content available'}
Published: {article.published_at}
Source: {article.source}
URL: {article.url}

DETECT EVENTS IN THESE CATEGORIES:

1. HEALTH TRENDS: Health conditions, outbreaks, or trends that increase demand for products
   Example: "Flu outbreak in Dublin" → impacts "Vitamins & Supplements"
   Example: "Skin condition trending on social media" → impacts "Cleanser", "Serum"

2. SUPPLY DISRUPTION: Shortages, recalls, or supply chain issues affecting products
   Example: "Vitamin shortage reported in Ireland"
   Example: "Cosmetics recall due to contamination"

3. REGULATORY CHANGE: New regulations affecting product sales
   Example: "New vitamin labeling requirements"
   Example: "FDA approves new OTC supplement"

4. VIRAL TREND: Social media trends, celebrity endorsements driving demand
   Example: "TikTok trend boosts vitamin C serum sales"
   Example: "Celebrity skincare routine goes viral"

5. COMPETITOR ACTION: Competitor promotions or actions affecting market
   Example: "Boots launches major vitamin promotion"
   Example: "New competitor pharmacy opens in Dublin"

CRITICAL RULES:
- ONLY detect events that DIRECTLY relate to our tracked products
- Extract ONLY facts - NO predictions about sales impact
- If article doesn't relate to our products, DO NOT use the tool
- Focus on events in Ireland/Dublin
- Be specific about which products are affected

REQUIRED FIELDS:
- event_type: One of the 5 categories above
- title: Clear event title
- description: What happened (facts only)
- severity: low/medium/high/critical
- confidence: low/medium/high
- urgency: immediate/within_week/within_month/future
- location: Where (if specified)
- key_facts: List of key facts from article
- potential_relevance: How this could affect our business (brief, factual)
- affected_products: List of product names from our tracked products that are affected
- affected_areas: List of locations/provinces affected

Example GOOD detection:
{{
  "event_type": "health_emergency",
  "title": "Norovirus Outbreak in Dublin Hospitals",
  "description": "Health officials confirm 80+ norovirus cases across Dublin hospitals",
  "severity": "high",
  "confidence": "high",
  "urgency": "immediate",
  "location": "Dublin, Ireland",
  "event_date": "2025-11-15",
  "key_facts": [
    "80+ confirmed cases",
    "Multiple hospitals affected",
    "HSE advises increased hygiene"
  ],
  "potential_relevance": "Norovirus outbreak may increase demand for vitamins, supplements, and hand hygiene products",
  "affected_products": ["Vitamins & Supplements"],
  "affected_areas": ["Dublin"],
  "source_url": "{article.url}",
  "published_at": "{article.published_at}"
}}

Example BAD detection (DON'T DO THIS):
{{
  "event_type": "health_emergency",
  "title": "Weather forecast sunny",
  "affected_products": ["Cleanser"],  ← NO! Weather doesn't directly affect cleanser demand
}}

Analyze this article. If it relates to our tracked products and matches one of the 5 event types, use the extract_event tool. Otherwise, respond with text explaining why it's not relevant.
"""

        # Call Claude with structured output
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}],
            tools=[{
                "name": "extract_event",
                "description": "Extract structured product-related event from article",
                "input_schema": DetectedEvent.model_json_schema()
            }]
        )

        # Parse structured output
        tool_use = next((block for block in response.content if block.type == "tool_use"), None)

        if tool_use:
            try:
                event = DetectedEvent(**tool_use.input)
                # Only return if it's a product-relevant event
                if event.event_type != "other" and event.affected_products:
                    return event
            except Exception as e:
                print(f"Error parsing event: {e}")
                return None

        return None

    def batch_detect_product_events(
        self,
        articles: List[NewsArticle],
        focus_products: List[str] = None,
        max_articles: int = 50
    ) -> List[DetectedEvent]:
        """
        Detect product events across multiple articles

        Args:
            articles: List of NewsArticles to analyze
            focus_products: Optional list of products to focus on
            max_articles: Maximum number of articles to process

        Returns:
            List of DetectedEvent objects
        """
        # Limit articles to control costs
        articles_to_process = articles[:max_articles]

        print(f"\nDetecting product events in {len(articles_to_process)} articles...")
        print(f"Tracked products: {', '.join(focus_products or list(self.tracked_products))}")
        print(f"Estimated cost: ${len(articles_to_process) * 0.003:.2f}")
        print()

        detected_events = []

        for i, article in enumerate(articles_to_process, 1):
            print(f"  [{i}/{len(articles_to_process)}] {article.title[:60]}...")

            result = self.detect_product_event(article, focus_products)

            if result.detected_event:
                event = result.detected_event
                detected_events.append(event)

                print(f"    ✓ EVENT: {event.event_type}")
                print(f"      Products: {', '.join(event.affected_products or ['None'])}")
                print(f"      Severity: {event.severity} | Confidence: {event.confidence}")
            else:
                if result.error:
                    print(f"    ✗ Error: {result.error}")
                else:
                    print(f"    - Not relevant to tracked products")

        print(f"\n{'=' * 60}")
        print(f"Detected {len(detected_events)} product-related events")
        print(f"{'=' * 60}")

        return detected_events

    def generate_product_alerts(
        self,
        events: List[DetectedEvent],
        severity_threshold: str = "medium"
    ) -> List[dict]:
        """
        Generate actionable alerts from detected events

        Args:
            events: List of DetectedEvent objects
            severity_threshold: Minimum severity to generate alert (low/medium/high/critical)

        Returns:
            List of alert dictionaries
        """
        severity_levels = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        threshold = severity_levels.get(severity_threshold, 1)

        alerts = []

        for event in events:
            event_severity = severity_levels.get(event.severity, 0)

            # Only generate alerts for events meeting severity threshold
            if event_severity >= threshold:
                alert = {
                    "alert_id": f"ALERT_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(alerts)+1}",
                    "event_type": event.event_type,
                    "title": event.title,
                    "severity": event.severity,
                    "urgency": event.urgency,
                    "affected_products": event.affected_products or [],
                    "affected_areas": event.affected_areas or [],
                    "location": event.location,
                    "event_date": event.event_date,
                    "description": event.description,
                    "key_facts": event.key_facts or [],
                    "potential_relevance": event.potential_relevance,
                    "source_url": event.source_url,
                    "detected_at": datetime.now().isoformat(),
                    "recommended_action": self._get_recommended_action(event)
                }

                alerts.append(alert)

        # Sort by severity (critical first)
        alerts.sort(key=lambda x: severity_levels.get(x['severity'], 0), reverse=True)

        return alerts

    def _get_recommended_action(self, event: DetectedEvent) -> str:
        """
        Get recommended action based on event type and severity

        Args:
            event: DetectedEvent object

        Returns:
            Recommended action string
        """
        actions = {
            "health_emergency": "Monitor demand for related health products. Consider increasing stock.",
            "supply_disruption": "Check inventory levels. Contact suppliers to confirm stock availability.",
            "regulatory_change": "Review affected products. Ensure compliance with new regulations.",
            "viral_trend": "Monitor social media and demand patterns. Consider promotional opportunities.",
            "competitor_action": "Review pricing and promotions. Monitor market share in affected areas.",
            "major_event": "Prepare for increased foot traffic in affected areas.",
            "weather_extreme": "Stock up on weather-related products. Ensure staff safety.",
            "economic_shock": "Monitor customer spending patterns. Adjust inventory accordingly."
        }

        base_action = actions.get(event.event_type, "Monitor situation and adjust strategy as needed.")

        # Add urgency modifier
        if event.urgency == "immediate":
            return f"URGENT: {base_action}"
        elif event.urgency == "within_week":
            return f"This week: {base_action}"
        else:
            return base_action


# Example usage
if __name__ == "__main__":
    from .models import NewsArticle

    # Test article
    test_article = NewsArticle(
        title="Vitamin D Shortage Hits Ireland as Winter Demand Surges",
        description="Pharmacies across Ireland report shortages of Vitamin D supplements as demand spikes during winter months. Health officials recommend alternative sources.",
        content="Irish pharmacies are experiencing unprecedented demand for Vitamin D supplements...",
        url="https://example.com/vitamin-shortage",
        published_at=datetime.now().isoformat(),
        source="Irish Times"
    )

    detector = ProductEventDetector()

    print("Testing product event detection...")
    result = detector.detect_product_event(test_article)

    if result.detected_event:
        event = result.detected_event
        print(f"\n✓ Event detected:")
        print(f"  Type: {event.event_type}")
        print(f"  Title: {event.title}")
        print(f"  Affected products: {', '.join(event.affected_products or [])}")
        print(f"  Severity: {event.severity}")
        print(f"  Confidence: {event.confidence}")

        # Generate alert
        alerts = detector.generate_product_alerts([event])
        if alerts:
            print(f"\n✓ Alert generated:")
            print(f"  Alert ID: {alerts[0]['alert_id']}")
            print(f"  Recommended action: {alerts[0]['recommended_action']}")
    else:
        print(f"\n✗ No product-related event detected")
        if result.error:
            print(f"  Error: {result.error}")
