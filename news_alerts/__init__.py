"""
News Alerts System for Black Swan Event Detection

Two-agent architecture:
1. Event Detector: Fetches news and detects events using LLM
2. Context Matcher: Matches events to business context for actionable alerts

Based on NEWS_ALERTS_REFOCUSED.md architecture.
"""

# Event Detection (Agent 1)
from .models import (
    DetectedEvent,
    NewsArticle,
    EventDetectionResult,
    DailyEventReport
)
from .news_fetcher import NewsFetcher
from .event_detector import EventDetectorAgent
from .event_storage import EventStorage

# Product-aware detection
from .top_products_loader import TopProductsLoader, LocationProducts
from .product_news_fetcher import ProductNewsFetcher
from .product_event_detector import ProductEventDetector

# Context Matching (Agent 2)
from .alert_models import (
    BusinessAlert,
    AlertDecision,
    DailyAlertReport,
    format_alert_for_display,
    format_daily_report
)
from .context_matcher import ContextMatcher
from .playbooks import (
    Playbook,
    PlaybookAction,
    get_playbook
)

__version__ = "0.2.0"

__all__ = [
    # Event Detection
    "DetectedEvent",
    "NewsArticle",
    "EventDetectionResult",
    "DailyEventReport",
    "NewsFetcher",
    "EventDetectorAgent",
    "EventStorage",
    # Product-aware detection
    "TopProductsLoader",
    "LocationProducts",
    "ProductNewsFetcher",
    "ProductEventDetector",
    # Context Matching
    "BusinessAlert",
    "AlertDecision",
    "DailyAlertReport",
    "format_alert_for_display",
    "format_daily_report",
    "ContextMatcher",
    "Playbook",
    "PlaybookAction",
    "get_playbook"
]
