"""
Pydantic models for structured event extraction from news articles.

Based on NEWS_ALERTS_REFOCUSED.md architecture.
"""

from pydantic import BaseModel, Field
from typing import List, Literal, Optional
from datetime import datetime


class DetectedEvent(BaseModel):
    """Structured event extracted from news article"""

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
    affected_products: List[str] = Field(default_factory=list)
    affected_areas: List[str] = Field(default_factory=list)
    expected_attendance: Optional[int] = None  # For events
    named_entities: List[str] = Field(default_factory=list)  # Companies, people, brands

    # Metadata
    source_url: str
    published_at: str
    confidence: Literal["low", "medium", "high"]
    urgency: Literal["immediate", "within_week", "within_month", "low"]

    # Key facts (NO predictions!)
    key_facts: List[str] = Field(default_factory=list)
    potential_relevance: str  # Why this might matter to retail pharmacy


class NewsArticle(BaseModel):
    """Raw news article before processing"""

    title: str
    description: Optional[str] = None
    content: Optional[str] = None
    url: str
    published_at: str
    source: str  # NewsAPI, Google News, Met Éireann, etc.
    author: Optional[str] = None


class EventDetectionResult(BaseModel):
    """Result of event detection process"""

    article: NewsArticle
    detected_event: Optional[DetectedEvent] = None
    detection_time: str
    processing_time_ms: float
    error: Optional[str] = None


class DailyEventReport(BaseModel):
    """Daily summary of detected events"""

    date: str
    total_articles_scanned: int
    events_detected: int
    alerts_generated: int
    events: List[DetectedEvent]
    processing_summary: dict
