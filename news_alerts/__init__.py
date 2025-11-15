"""
News Alerts System for Black Swan Event Detection

Fetches news from multiple sources and detects events that could affect
a retail pharmacy business using LLM-based structured extraction.

Based on NEWS_ALERTS_REFOCUSED.md architecture.
"""

from .models import (
    DetectedEvent,
    NewsArticle,
    EventDetectionResult,
    DailyEventReport
)
from .news_fetcher import NewsFetcher
from .event_detector import EventDetectorAgent
from .event_storage import EventStorage

__version__ = "0.1.0"

__all__ = [
    "DetectedEvent",
    "NewsArticle",
    "EventDetectionResult",
    "DailyEventReport",
    "NewsFetcher",
    "EventDetectorAgent",
    "EventStorage"
]
