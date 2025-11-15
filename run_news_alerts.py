#!/usr/bin/env python3
"""
News Alerts CLI - Fetch news and detect events

Usage:
    python run_news_alerts.py                    # Run with default settings
    python run_news_alerts.py --health-only      # Only health emergencies
    python run_news_alerts.py --events-only      # Only major events
    python run_news_alerts.py --demo             # Demo mode with test article
    python run_news_alerts.py --stats            # Show storage stats
"""

import argparse
import os
from datetime import date, datetime
from news_alerts import (
    NewsFetcher,
    EventDetectorAgent,
    EventStorage,
    DailyEventReport,
    NewsArticle
)


def run_detection(
    focus_type: str = "all",
    newsapi_key: str = None,
    anthropic_key: str = None,
    max_articles: int = 50
):
    """
    Main detection pipeline

    Args:
        focus_type: "all", "health", or "events"
        newsapi_key: Optional NewsAPI key
        anthropic_key: Optional Anthropic API key
        max_articles: Maximum number of articles to process (default: 50)
    """
    print("=" * 80)
    print("NEWS ALERTS - Event Detection Pipeline")
    print("=" * 80)
    print(f"Date: {date.today().isoformat()}")
    print(f"Focus: {focus_type}")
    print(f"Max articles: {max_articles}")
    print()

    # Initialize components
    print("Initializing components...")
    fetcher = NewsFetcher(newsapi_key=newsapi_key)
    detector = EventDetectorAgent(api_key=anthropic_key)
    storage = EventStorage()

    # Fetch news
    print("\nFetching news articles...")
    articles = []

    if focus_type in ["all", "health"]:
        print("  - Fetching health news...")
        health_articles = fetcher.fetch_irish_health_news()
        articles.extend(health_articles)
        print(f"    Found {len(health_articles)} health articles")

    if focus_type in ["all", "events"]:
        print("  - Fetching event news...")
        event_articles = fetcher.fetch_dublin_events_news()
        articles.extend(event_articles)
        print(f"    Found {len(event_articles)} event articles")

    if focus_type == "all":
        print("  - Fetching weather alerts...")
        weather_articles = fetcher.fetch_met_eireann()
        articles.extend(weather_articles)
        print(f"    Found {len(weather_articles)} weather alerts")

    print(f"\nTotal articles fetched: {len(articles)}")

    if len(articles) == 0:
        print("\nNo articles found. Exiting.")
        return

    # Limit number of articles to process
    if len(articles) > max_articles:
        print(f"⚠️  Limiting to {max_articles} articles to control API costs")
        print(f"   (Use --max-articles to adjust this limit)")
        articles = articles[:max_articles]

    print(f"Processing {len(articles)} articles...")

    # Detect events
    print("\nDetecting events (this may take a few minutes)...")
    print(f"Estimated cost: ${len(articles) * 0.003:.2f} (at ~$0.003/article)")
    print()

    detected_events = []
    event_types_to_detect = []

    if focus_type == "health":
        event_types_to_detect = ["health_emergency"]
    elif focus_type == "events":
        event_types_to_detect = ["major_event"]
    else:
        event_types_to_detect = ["health_emergency", "major_event"]

    for i, article in enumerate(articles, 1):
        print(f"  Processing article {i}/{len(articles)}: {article.title[:60]}...")

        try:
            result = detector.detect_event(article, event_types=event_types_to_detect)

            if result.detected_event:
                detected_events.append(result.detected_event)
                print(f"    ✓ Event detected: {result.detected_event.event_type} ({result.detected_event.severity})")

                # Save immediately
                storage.save_event(result.detected_event)
            else:
                if result.error:
                    print(f"    ✗ Error: {result.error}")
                else:
                    print(f"    - No event detected")

        except Exception as e:
            print(f"    ✗ Exception: {e}")

    # Generate daily report
    print("\n" + "=" * 80)
    print("DETECTION SUMMARY")
    print("=" * 80)
    print(f"Articles scanned: {len(articles)}")
    print(f"Events detected: {len(detected_events)}")
    print()

    if detected_events:
        print("Detected Events:")
        print("-" * 80)

        for event in detected_events:
            print(f"\n{event.event_type.upper()}: {event.title}")
            print(f"  Severity: {event.severity} | Confidence: {event.confidence} | Urgency: {event.urgency}")
            print(f"  Location: {event.location or 'N/A'}")
            print(f"  Date: {event.event_date or 'N/A'}")
            print(f"  Relevance: {event.potential_relevance}")
            print(f"  Source: {event.source_url}")

        # Save daily report
        report = DailyEventReport(
            date=date.today().isoformat(),
            total_articles_scanned=len(articles),
            events_detected=len(detected_events),
            alerts_generated=len([e for e in detected_events if e.severity in ["high", "critical"]]),
            events=detected_events,
            processing_summary={
                "focus_type": focus_type,
                "event_types_detected": list(set(e.event_type for e in detected_events))
            }
        )

        storage.save_daily_report(report)
        print("\n" + "=" * 80)
        print(f"Report saved to: data/events/report_{date.today().isoformat()}.json")

    else:
        print("No events detected today.")

    print("=" * 80)


def run_demo():
    """Run demo with sample articles"""
    print("=" * 80)
    print("DEMO MODE - Testing Event Detection")
    print("=" * 80)

    # Sample articles
    test_articles = [
        NewsArticle(
            title="Norovirus Outbreak Spreads Across Dublin Hospitals",
            description="Health officials confirm over 80 cases of norovirus across three major Dublin hospitals in the past week. HSE advises increased hygiene measures.",
            content="Dublin health authorities are managing a significant norovirus outbreak affecting St. James's Hospital, Beaumont Hospital, and the Mater Hospital...",
            url="https://example.com/norovirus-outbreak",
            published_at=datetime.now().isoformat(),
            source="Irish Times"
        ),
        NewsArticle(
            title="Ed Sheeran Announces 3Arena Concert Dates",
            description="Ed Sheeran will perform three nights at Dublin's 3Arena in June 2025. Expected attendance of 42,000 across all shows.",
            content="International pop star Ed Sheeran has announced a three-night residency at Dublin's 3Arena for June 20-22, 2025...",
            url="https://example.com/ed-sheeran-concert",
            published_at=datetime.now().isoformat(),
            source="RTE News"
        ),
        NewsArticle(
            title="Dublin Weather Forecast Shows Sunny Skies This Weekend",
            description="Met Éireann predicts pleasant weekend weather with temperatures around 18°C.",
            content="This weekend will see pleasant conditions across Dublin with sunny periods...",
            url="https://example.com/weather",
            published_at=datetime.now().isoformat(),
            source="Met Éireann"
        )
    ]

    # Initialize detector
    print("\nInitializing event detector...")
    detector = EventDetectorAgent()
    storage = EventStorage()

    print(f"\nTesting with {len(test_articles)} sample articles:")
    print()

    detected_events = []

    for i, article in enumerate(test_articles, 1):
        print(f"{i}. Testing: {article.title}")
        print(f"   Source: {article.source}")

        result = detector.detect_event(article, event_types=["health_emergency", "major_event"])

        if result.detected_event:
            event = result.detected_event
            detected_events.append(event)

            print(f"   ✓ DETECTED: {event.event_type}")
            print(f"     Severity: {event.severity}")
            print(f"     Confidence: {event.confidence}")
            print(f"     Urgency: {event.urgency}")
            print(f"     Relevance: {event.potential_relevance}")

            # Save event
            storage.save_event(event)
        else:
            print(f"   - No event detected (likely not relevant)")

        print()

    print("=" * 80)
    print(f"Demo complete. Detected {len(detected_events)} events.")
    print("=" * 80)


def show_stats():
    """Show storage statistics"""
    storage = EventStorage()
    storage.print_stats()

    # Show recent events
    recent_events = storage.get_recent_events(days=7)

    if recent_events:
        print("\nRecent Events (last 7 days):")
        print("-" * 60)

        for event in recent_events:
            print(f"{event.event_type}: {event.title}")
            print(f"  Severity: {event.severity} | Date: {event.event_date or 'N/A'}")
            print()


def main():
    parser = argparse.ArgumentParser(
        description="News Alerts - Detect black swan events from news"
    )

    parser.add_argument(
        "--health-only",
        action="store_true",
        help="Only detect health emergencies"
    )

    parser.add_argument(
        "--events-only",
        action="store_true",
        help="Only detect major events (concerts, festivals, etc.)"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo mode with sample articles"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show storage statistics"
    )

    parser.add_argument(
        "--newsapi-key",
        type=str,
        help="NewsAPI.org API key (optional, can also use NEWS_API_KEY env var)"
    )

    parser.add_argument(
        "--anthropic-key",
        type=str,
        help="Anthropic API key (optional, can also use ANTHROPIC_API_KEY env var)"
    )

    parser.add_argument(
        "--max-articles",
        type=int,
        default=50,
        help="Maximum number of articles to process (default: 50, controls API costs)"
    )

    args = parser.parse_args()

    # Handle different modes
    if args.demo:
        run_demo()
    elif args.stats:
        show_stats()
    else:
        # Determine focus type
        focus_type = "all"
        if args.health_only:
            focus_type = "health"
        elif args.events_only:
            focus_type = "events"

        # Run detection
        run_detection(
            focus_type=focus_type,
            newsapi_key=args.newsapi_key,
            anthropic_key=args.anthropic_key,
            max_articles=args.max_articles
        )


if __name__ == "__main__":
    main()
