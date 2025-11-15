#!/usr/bin/env python3
"""
Historical Alert Analysis Tool

Analyzes past alerts to identify trends, patterns, and insights.

Usage:
    python analyze_alerts.py
    python analyze_alerts.py --days 30
    python analyze_alerts.py --export report.json
"""

import argparse
import json
from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict, Counter
from typing import List, Dict, Any


def load_all_alerts(days_back: int = 30) -> List[Dict]:
    """Load all alerts from the last N days"""
    alerts = []
    alert_dir = Path("data/alerts")

    if not alert_dir.exists():
        return alerts

    # Calculate date range
    end_date = date.today()
    start_date = end_date - timedelta(days=days_back)

    # Load alert files
    for alert_file in sorted(alert_dir.glob("alert_*.json")):
        try:
            with open(alert_file, 'r') as f:
                alert = json.load(f)

                # Extract date from generated_at
                gen_date = datetime.fromisoformat(alert['generated_at']).date()

                if start_date <= gen_date <= end_date:
                    alerts.append(alert)
        except Exception as e:
            print(f"⚠️  Could not load {alert_file.name}: {e}")

    return alerts


def analyze_trends(alerts: List[Dict]) -> Dict[str, Any]:
    """Analyze alert trends"""

    analysis = {
        "summary": {},
        "by_type": {},
        "by_severity": {},
        "by_confidence": {},
        "by_location": {},
        "by_category": {},
        "timeline": {},
        "insights": []
    }

    if not alerts:
        return analysis

    # Basic counts
    analysis["summary"] = {
        "total_alerts": len(alerts),
        "date_range": {
            "start": min(alert["generated_at"] for alert in alerts),
            "end": max(alert["generated_at"] for alert in alerts)
        }
    }

    # By alert type
    type_counts = Counter(alert["alert_type"] for alert in alerts)
    analysis["by_type"] = dict(type_counts)

    # By severity
    severity_counts = Counter(alert["severity"] for alert in alerts)
    analysis["by_severity"] = dict(severity_counts)

    # By confidence level
    confidence_buckets = defaultdict(int)
    for alert in alerts:
        conf = alert["decision"]["confidence"]
        if conf >= 0.9:
            confidence_buckets["Very High (90%+)"] += 1
        elif conf >= 0.75:
            confidence_buckets["High (75-90%)"] += 1
        elif conf >= 0.60:
            confidence_buckets["Medium (60-75%)"] += 1
        else:
            confidence_buckets["Low (<60%)"] += 1
    analysis["by_confidence"] = dict(confidence_buckets)

    # By location
    location_counts = Counter()
    for alert in alerts:
        for loc in alert.get("affected_locations", []):
            location_counts[loc] += 1
    analysis["by_location"] = dict(location_counts.most_common(10))

    # By category
    category_counts = Counter()
    for alert in alerts:
        for cat in alert.get("affected_categories", []):
            category_counts[cat] += 1
    analysis["by_category"] = dict(category_counts.most_common(10))

    # Timeline (by day)
    timeline = defaultdict(int)
    for alert in alerts:
        alert_date = datetime.fromisoformat(alert["generated_at"]).date().isoformat()
        timeline[alert_date] += 1
    analysis["timeline"] = dict(sorted(timeline.items()))

    # Generate insights
    insights = []

    # Most common alert type
    if analysis["by_type"]:
        top_type, count = type_counts.most_common(1)[0]
        pct = (count / len(alerts)) * 100
        insights.append(f"Most common alert type: {top_type} ({count} alerts, {pct:.1f}%)")

    # Severity distribution
    critical_count = severity_counts.get("critical", 0)
    if critical_count > 0:
        critical_pct = (critical_count / len(alerts)) * 100
        insights.append(f"Critical alerts: {critical_count} ({critical_pct:.1f}% of total)")

    # High confidence alerts
    high_conf_count = confidence_buckets.get("Very High (90%+)", 0)
    if high_conf_count > 0:
        high_conf_pct = (high_conf_count / len(alerts)) * 100
        insights.append(f"High confidence alerts: {high_conf_count} ({high_conf_pct:.1f}% - data-driven decisions)")

    # Busiest location
    if analysis["by_location"]:
        top_location, count = list(analysis["by_location"].items())[0]
        insights.append(f"Most impacted location: {top_location} ({count} alerts)")

    # Most affected category
    if analysis["by_category"]:
        top_category, count = list(analysis["by_category"].items())[0]
        insights.append(f"Most affected category: {top_category} ({count} alerts)")

    # Busiest day
    if timeline:
        busiest_day = max(timeline.items(), key=lambda x: x[1])
        insights.append(f"Busiest day: {busiest_day[0]} ({busiest_day[1]} alerts)")

    analysis["insights"] = insights

    return analysis


def print_analysis(analysis: Dict[str, Any]):
    """Print analysis in a readable format"""

    print("\n" + "=" * 80)
    print("HISTORICAL ALERT ANALYSIS")
    print("=" * 80)

    # Summary
    print("\n📊 SUMMARY")
    print(f"   Total Alerts: {analysis['summary'].get('total_alerts', 0)}")
    if "date_range" in analysis["summary"]:
        dr = analysis["summary"]["date_range"]
        print(f"   Date Range: {dr['start'][:10]} to {dr['end'][:10]}")

    # Insights
    if analysis["insights"]:
        print("\n💡 KEY INSIGHTS")
        for insight in analysis["insights"]:
            print(f"   • {insight}")

    # By Type
    if analysis["by_type"]:
        print("\n📈 ALERTS BY TYPE")
        for alert_type, count in sorted(analysis["by_type"].items(), key=lambda x: x[1], reverse=True):
            bar = "█" * min(count, 50)
            print(f"   {alert_type:20s} {bar} {count}")

    # By Severity
    if analysis["by_severity"]:
        print("\n⚠️  ALERTS BY SEVERITY")
        severity_order = ["critical", "high", "moderate", "low"]
        for severity in severity_order:
            count = analysis["by_severity"].get(severity, 0)
            if count > 0:
                emoji = {"critical": "🚨", "high": "⚠️ ", "moderate": "ℹ️ ", "low": "📝"}
                bar = "█" * min(count, 50)
                print(f"   {emoji.get(severity, '')} {severity:12s} {bar} {count}")

    # By Confidence
    if analysis["by_confidence"]:
        print("\n🎯 CONFIDENCE DISTRIBUTION")
        conf_order = ["Very High (90%+)", "High (75-90%)", "Medium (60-75%)", "Low (<60%)"]
        for conf_level in conf_order:
            count = analysis["by_confidence"].get(conf_level, 0)
            if count > 0:
                bar = "█" * min(count, 50)
                print(f"   {conf_level:20s} {bar} {count}")

    # Top Locations
    if analysis["by_location"]:
        print("\n📍 TOP IMPACTED LOCATIONS")
        for location, count in list(analysis["by_location"].items())[:5]:
            bar = "█" * min(count, 30)
            print(f"   {location:20s} {bar} {count}")

    # Top Categories
    if analysis["by_category"]:
        print("\n🏷️  TOP AFFECTED CATEGORIES")
        for category, count in list(analysis["by_category"].items())[:5]:
            bar = "█" * min(count, 30)
            print(f"   {category:30s} {bar} {count}")

    # Timeline
    if analysis["timeline"]:
        print("\n📅 TIMELINE (Last 10 Days)")
        items = sorted(analysis["timeline"].items(), reverse=True)[:10]
        for alert_date, count in items:
            bar = "█" * min(count, 40)
            print(f"   {alert_date} {bar} {count}")

    print("\n" + "=" * 80)


def export_analysis(analysis: Dict[str, Any], output_file: str):
    """Export analysis to JSON file"""
    with open(output_file, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"\n✅ Analysis exported to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Analyze historical alert patterns and trends"
    )

    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Number of days to analyze (default: 30)"
    )

    parser.add_argument(
        "--export",
        type=str,
        help="Export analysis to JSON file"
    )

    args = parser.parse_args()

    # Load alerts
    print(f"\nLoading alerts from last {args.days} days...")
    alerts = load_all_alerts(days_back=args.days)

    if not alerts:
        print(f"\n⚠️  No alerts found in the last {args.days} days.")
        print("   Run the pipeline to generate some alerts first:")
        print("   python run_full_pipeline.py")
        return

    print(f"✓ Loaded {len(alerts)} alerts")

    # Analyze
    analysis = analyze_trends(alerts)

    # Display
    print_analysis(analysis)

    # Export if requested
    if args.export:
        export_analysis(analysis, args.export)

    # Recommendations
    print("\n💼 RECOMMENDATIONS")

    critical_count = analysis["by_severity"].get("critical", 0)
    if critical_count > 0:
        print(f"   • Review {critical_count} critical alert(s) to ensure actions were taken")

    low_conf_count = analysis["by_confidence"].get("Low (<60%)", 0)
    if low_conf_count > 0:
        print(f"   • {low_conf_count} low-confidence alerts - consider enabling --use-real-data for better accuracy")

    if not analysis["by_confidence"].get("Very High (90%+)", 0):
        print("   • No high-confidence alerts detected - enable data-driven mode with --use-real-data")

    print()


if __name__ == "__main__":
    main()
