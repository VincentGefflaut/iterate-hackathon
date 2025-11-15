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
