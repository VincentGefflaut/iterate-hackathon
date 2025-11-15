#!/usr/bin/env python3
"""
Product Alerts MVP - Integrated pipeline for top products news alerts

Integrates top.csv data with news fetching and event detection to generate
product-specific alerts for today's date.

Usage:
    python run_product_alerts_mvp.py                 # Run for today with default settings
    python run_product_alerts_mvp.py --top-n 10      # Use top 10 locations
    python run_product_alerts_mvp.py --max-articles 100  # Process up to 100 articles
    python run_product_alerts_mvp.py --demo          # Demo mode (test with sample data)
"""

import argparse
import os
import json
from datetime import date, datetime
from pathlib import Path
from typing import List

from news_alerts import (
    ProductNewsFetcher,
    ProductEventDetector,
    EventStorage,
    TopProductsLoader,
    LocationProducts
)


def print_header(title: str):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_section(title: str):
    """Print formatted section"""
    print("\n" + "-" * 80)
    print(f"  {title}")
    print("-" * 80)


def run_mvp_pipeline(
    top_n_locations: int = 5,
    max_articles: int = 50,
    severity_threshold: str = "medium"
):
    """
    Run the complete product alerts MVP pipeline

    Args:
        top_n_locations: Number of top locations to monitor
        max_articles: Maximum articles to process
        severity_threshold: Minimum severity for alerts (low/medium/high/critical)
    """
    print_header("PRODUCT ALERTS MVP - INTEGRATED PIPELINE")

    print(f"📅 Date: {date.today().isoformat()}")
    print(f"📍 Monitoring: Top {top_n_locations} locations by sales volume")
    print(f"📰 Max articles: {max_articles}")
    print(f"⚠️  Alert threshold: {severity_threshold}")
    print()

    # =========================================================================
    # STEP 1: Load top products data
    # =========================================================================
    print_section("STEP 1: Load Top Products Data")

    try:
        loader = TopProductsLoader()
        top_locations = loader.get_top_locations(top_n_locations)
        unique_products = loader.get_unique_products()

        print(f"✓ Loaded data for {len(loader.get_all_locations())} locations")
        print(f"✓ Tracking {len(unique_products)} unique products: {', '.join(sorted(unique_products))}")
        print()

        print("Top locations to monitor:")
        for i, loc in enumerate(top_locations, 1):
            print(f"  {i}. {loc.location_name} ({loc.total_sold:,} sales)")
            print(f"     Top products: {', '.join(loc.top_products)}")

    except Exception as e:
        print(f"❌ Error loading top products: {e}")
        return

    # =========================================================================
    # STEP 2: Fetch product-related news
    # =========================================================================
    print_section("STEP 2: Fetch Product-Related News")

    # Check for API key
    newsapi_key = os.getenv("NEWS_API_KEY")
    if not newsapi_key:
        print("⚠️  NEWS_API_KEY not set. Limited to free RSS feeds.")
        print("   Set NEWS_API_KEY in .env for better results.")

    try:
        fetcher = ProductNewsFetcher(newsapi_key=newsapi_key)

        # Fetch health and product news
        print(f"\nFetching news for top {top_n_locations} locations...")
        articles = fetcher.fetch_health_and_product_news(
            top_n_locations=top_n_locations,
            days_back=1
        )

        print(f"\n✓ Fetched {len(articles)} unique articles")

        if len(articles) == 0:
            print("\n⚠️  No articles found. Try:")
            print("   1. Set NEWS_API_KEY in .env")
            print("   2. Check internet connection")
            print("   3. Run with --demo flag for testing")
            return

        # Limit to max_articles
        if len(articles) > max_articles:
            print(f"⚠️  Limiting to {max_articles} articles to control API costs")
            articles = articles[:max_articles]

        print(f"\nProcessing {len(articles)} articles...")

    except Exception as e:
        print(f"❌ Error fetching news: {e}")
        return

    # =========================================================================
    # STEP 3: Detect product-related events
    # =========================================================================
    print_section("STEP 3: Detect Product-Related Events")

    # Check for Anthropic API key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not set in environment")
        print("   Set it in .env file or export ANTHROPIC_API_KEY=your-key")
        return

    try:
        detector = ProductEventDetector(api_key=anthropic_key)
        storage = EventStorage()

        # Detect events
        events = detector.batch_detect_product_events(
            articles=articles,
            focus_products=list(unique_products),
            max_articles=max_articles
        )

        print(f"\n✓ Detected {len(events)} product-related events")

        # Save events
        for event in events:
            storage.save_event(event)

        if events:
            print("\nDetected events summary:")
            for i, event in enumerate(events, 1):
                print(f"\n  {i}. {event.event_type.upper()}: {event.title}")
                print(f"     Severity: {event.severity} | Confidence: {event.confidence}")
                print(f"     Products: {', '.join(event.affected_products or ['None'])}")
                print(f"     Location: {event.location or 'N/A'}")

    except Exception as e:
        print(f"❌ Error detecting events: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # STEP 4: Generate alerts
    # =========================================================================
    print_section("STEP 4: Generate Product Alerts")

    try:
        alerts = detector.generate_product_alerts(
            events=events,
            severity_threshold=severity_threshold
        )

        print(f"\n✓ Generated {len(alerts)} alerts (severity >= {severity_threshold})")

        if alerts:
            # Save alerts to file
            alerts_dir = Path("data/alerts")
            alerts_dir.mkdir(parents=True, exist_ok=True)

            alerts_file = alerts_dir / f"product_alerts_{date.today().isoformat()}.json"

            with open(alerts_file, 'w') as f:
                json.dump({
                    "date": date.today().isoformat(),
                    "generated_at": datetime.now().isoformat(),
                    "total_alerts": len(alerts),
                    "severity_threshold": severity_threshold,
                    "tracked_locations": [loc.location_name for loc in top_locations],
                    "tracked_products": list(unique_products),
                    "alerts": alerts
                }, f, indent=2)

            print(f"✓ Alerts saved to: {alerts_file}")

            # Display alerts
            print("\n" + "=" * 80)
            print("  PRODUCT ALERTS")
            print("=" * 80)

            for i, alert in enumerate(alerts, 1):
                print(f"\n🚨 ALERT #{i}")
                print(f"   ID: {alert['alert_id']}")
                print(f"   Type: {alert['event_type']} | Severity: {alert['severity']} | Urgency: {alert['urgency']}")
                print(f"   Title: {alert['title']}")
                print(f"   Affected Products: {', '.join(alert['affected_products'])}")
                print(f"   Affected Areas: {', '.join(alert['affected_areas']) if alert['affected_areas'] else 'N/A'}")
                print(f"   Location: {alert['location'] or 'N/A'}")
                print(f"   Event Date: {alert['event_date'] or 'N/A'}")
                print(f"\n   Description:")
                print(f"   {alert['description']}")
                print(f"\n   Key Facts:")
                for fact in alert['key_facts']:
                    print(f"     • {fact}")
                print(f"\n   Potential Impact:")
                print(f"   {alert['potential_relevance']}")
                print(f"\n   Recommended Action:")
                print(f"   {alert['recommended_action']}")
                print(f"\n   Source: {alert['source_url']}")
                print("   " + "-" * 76)

        else:
            print("\nℹ️  No alerts generated (no events met severity threshold)")

    except Exception as e:
        print(f"❌ Error generating alerts: {e}")
        import traceback
        traceback.print_exc()
        return

    # =========================================================================
    # Summary
    # =========================================================================
    print_header("✅ MVP PIPELINE COMPLETE")

    print("📊 Summary:")
    print(f"   • Locations monitored: {len(top_locations)}")
    print(f"   • Products tracked: {len(unique_products)}")
    print(f"   • Articles analyzed: {len(articles)}")
    print(f"   • Events detected: {len(events)}")
    print(f"   • Alerts generated: {len(alerts)}")
    print()

    if alerts:
        # Count by severity
        severity_counts = {}
        for alert in alerts:
            sev = alert['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1

        print("📈 Alerts by severity:")
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            if count > 0:
                emoji = "🔴" if severity == "critical" else "🟠" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                print(f"   {emoji} {severity.capitalize()}: {count}")

        # Count by product
        product_counts = {}
        for alert in alerts:
            for product in alert['affected_products']:
                product_counts[product] = product_counts.get(product, 0) + 1

        if product_counts:
            print("\n📦 Alerts by product:")
            for product, count in sorted(product_counts.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {product}: {count}")

        print()
        print(f"📄 View alerts: cat {alerts_file}")

    print("\n🎯 Next steps:")
    print("   • Review alerts and take recommended actions")
    print("   • Monitor demand patterns for affected products")
    print("   • Check inventory levels for high-severity alerts")
    print("   • Communicate with stores in affected areas")
    print()


def run_demo():
    """Run demo mode with sample data"""
    print_header("DEMO MODE - Testing Product Alerts MVP")

    print("This demo will test the pipeline with sample product-related news.")
    print()

    from news_alerts.models import NewsArticle

    # Sample product-related articles
    demo_articles = [
        NewsArticle(
            title="Vitamin D Shortage Hits Irish Pharmacies as Winter Demand Surges",
            description="Pharmacies across Dublin, Cork, and Galway report shortages of Vitamin D supplements. Health officials recommend alternative sources as suppliers struggle to meet demand.",
            content="Irish pharmacies are experiencing unprecedented demand for Vitamin D supplements as winter approaches. Multiple chains in Dublin, Cork, and Galway have reported stock shortages...",
            url="https://example.com/vitamin-shortage",
            published_at=datetime.now().isoformat(),
            source="Irish Independent"
        ),
        NewsArticle(
            title="Viral TikTok Trend Drives Serum Sales in Ireland",
            description="A viral skincare routine featuring vitamin C serum has led to a 300% increase in sales across Irish beauty retailers. Dublin stores report selling out within hours.",
            content="Irish beauty retailers are scrambling to restock as a TikTok skincare trend goes viral. The #GlowUp2025 trend features vitamin C serum as the key ingredient...",
            url="https://example.com/serum-trend",
            published_at=datetime.now().isoformat(),
            source="RTE News"
        ),
        NewsArticle(
            title="New Cleanser Product Recall Announced in Ireland",
            description="The HPRA has issued a recall for several cleanser products due to contamination concerns. Retailers advised to remove affected products from shelves immediately.",
            content="The Health Products Regulatory Authority has issued an urgent recall for several cleanser products sold in Ireland...",
            url="https://example.com/cleanser-recall",
            published_at=datetime.now().isoformat(),
            source="Irish Times"
        )
    ]

    print_section("Demo Articles")
    for i, article in enumerate(demo_articles, 1):
        print(f"{i}. {article.title}")
        print(f"   Source: {article.source}")
        print()

    # Check for API key
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if not anthropic_key:
        print("❌ ANTHROPIC_API_KEY not set")
        print("   Set it in .env file to run demo")
        return

    print_section("Detecting Events")

    try:
        loader = TopProductsLoader()
        detector = ProductEventDetector(api_key=anthropic_key)

        events = detector.batch_detect_product_events(
            articles=demo_articles,
            max_articles=10
        )

        print(f"\n✓ Detected {len(events)} events from demo articles")

        if events:
            alerts = detector.generate_product_alerts(events, severity_threshold="low")

            print(f"✓ Generated {len(alerts)} alerts")

            for i, alert in enumerate(alerts, 1):
                print(f"\n🚨 ALERT #{i}: {alert['title']}")
                print(f"   Products: {', '.join(alert['affected_products'])}")
                print(f"   Severity: {alert['severity']}")
                print(f"   Action: {alert['recommended_action']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

    print_header("✅ DEMO COMPLETE")


def main():
    parser = argparse.ArgumentParser(
        description="Product Alerts MVP - Integrated news alerts for top products",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--top-n",
        type=int,
        default=5,
        help="Number of top locations to monitor (default: 5)"
    )

    parser.add_argument(
        "--max-articles",
        type=int,
        default=50,
        help="Maximum number of articles to process (default: 50, controls API costs)"
    )

    parser.add_argument(
        "--severity",
        choices=["low", "medium", "high", "critical"],
        default="medium",
        help="Minimum severity for alerts (default: medium)"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with sample data"
    )

    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_mvp_pipeline(
            top_n_locations=args.top_n,
            max_articles=args.max_articles,
            severity_threshold=args.severity
        )


if __name__ == "__main__":
    main()
