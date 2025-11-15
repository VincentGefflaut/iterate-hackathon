#!/usr/bin/env python3
"""
Context Matcher CLI - Generate business alerts from detected events

This is Phase 2 of the News Alerts system:
- Phase 1: Event Detector (run_news_alerts.py) → Detected Events
- Phase 2: Context Matcher (this script) → Business Alerts

Usage:
    python run_context_matcher.py                    # Process today's events
    python run_context_matcher.py --date 2024-11-15  # Process specific date
    python run_context_matcher.py --stats             # Show alert statistics
"""

import argparse
import json
from datetime import date, datetime
from pathlib import Path

from news_alerts import EventStorage
from news_alerts.context_matcher import ContextMatcher
from news_alerts.alert_models import format_alert_for_display, DailyAlertReport, format_daily_report


def run_context_matching(target_date: date = None, save_alerts: bool = True):
    """
    Run context matching on detected events

    Args:
        target_date: Date to process (default: today)
        save_alerts: Whether to save alerts to files
    """
    if target_date is None:
        target_date = date.today()

    print("=" * 80)
    print("CONTEXT MATCHER - Business Alert Generation")
    print("=" * 80)
    print(f"Date: {target_date.isoformat()}")
    print()

    # Initialize matcher
    print("Initializing Context Matcher...")
    matcher = ContextMatcher(use_real_data=False)

    # Evaluate events
    print(f"\nEvaluating events for {target_date.isoformat()}...")
    alerts = matcher.evaluate_events(target_date)

    print("\n" + "=" * 80)
    print("MATCHING RESULTS")
    print("=" * 80)
    print(f"Alerts Generated: {len(alerts)}")
    print()

    if not alerts:
        print("No actionable alerts generated.")
        print("This could mean:")
        print("  - No events were detected for this date")
        print("  - Detected events did not meet alert criteria")
        print("  - Events were outside our business scope")
        return

    # Summarize alerts
    alerts_by_severity = {}
    alerts_by_type = {}

    for alert in alerts:
        alerts_by_severity[alert.severity] = alerts_by_severity.get(alert.severity, 0) + 1
        alerts_by_type[alert.alert_type] = alerts_by_type.get(alert.alert_type, 0) + 1

    print("Alerts by Severity:")
    for severity, count in sorted(alerts_by_severity.items()):
        print(f"  {severity}: {count}")
    print()

    print("Alerts by Type:")
    for alert_type, count in sorted(alerts_by_type.items()):
        print(f"  {alert_type}: {count}")
    print()

    # Display each alert
    print("=" * 80)
    print("GENERATED ALERTS")
    print("=" * 80)
    print()

    for i, alert in enumerate(alerts, 1):
        print(f"ALERT {i}/{len(alerts)}")
        print(format_alert_for_display(alert))
        print()

    # Save alerts
    if save_alerts:
        save_dir = Path("data/alerts")
        save_dir.mkdir(parents=True, exist_ok=True)

        # Save individual alerts
        for alert in alerts:
            alert_file = save_dir / f"alert_{target_date.isoformat()}_{alert.alert_id[:8]}.json"
            with open(alert_file, 'w') as f:
                json.dump(alert.model_dump(), f, indent=2)

        print(f"✓ Saved {len(alerts)} alerts to {save_dir}/")
        print()

        # Create daily report
        storage = EventStorage()
        detected_events = storage.load_events(target_date)

        summary_lines = []
        summary_lines.append(f"Evaluated {len(detected_events)} detected events.")
        summary_lines.append(f"Generated {len(alerts)} actionable business alerts.")

        critical_count = alerts_by_severity.get("critical", 0)
        high_count = alerts_by_severity.get("high", 0)

        if critical_count > 0:
            summary_lines.append(f"⚠️  {critical_count} CRITICAL alerts require immediate attention.")
        if high_count > 0:
            summary_lines.append(f"⚠️  {high_count} HIGH priority alerts need action today.")

        # Recommended priorities
        priorities = []
        for alert in sorted(alerts, key=lambda a: ("critical", "high", "moderate", "low").index(a.severity)):
            if alert.severity in ["critical", "high"]:
                priorities.append(f"[{alert.severity.upper()}] {alert.event_title}")

        report = DailyAlertReport(
            report_date=target_date.isoformat(),
            total_events_evaluated=len(detected_events),
            alerts_generated=len(alerts),
            alerts_by_severity=alerts_by_severity,
            alerts_by_type=alerts_by_type,
            alerts=alerts,
            summary="\n".join(summary_lines),
            recommended_priorities=priorities[:5]  # Top 5
        )

        report_file = save_dir / f"daily_report_{target_date.isoformat()}.json"
        with open(report_file, 'w') as f:
            json.dump(report.model_dump(), f, indent=2)

        print(f"✓ Saved daily report to {report_file}")
        print()

        # Print daily report
        print(format_daily_report(report))


def show_statistics():
    """Show alert statistics"""
    alert_dir = Path("data/alerts")

    if not alert_dir.exists():
        print("No alerts found. Run context matcher first.")
        return

    alert_files = list(alert_dir.glob("alert_*.json"))
    report_files = list(alert_dir.glob("daily_report_*.json"))

    print("=" * 80)
    print("ALERT STATISTICS")
    print("=" * 80)
    print(f"Alert files: {len(alert_files)}")
    print(f"Daily reports: {len(report_files)}")
    print()

    if report_files:
        print("Recent Reports:")
        for report_file in sorted(report_files, reverse=True)[:5]:
            with open(report_file, 'r') as f:
                report = json.load(f)
            print(f"  {report['report_date']}: {report['alerts_generated']} alerts")

    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Context Matcher - Generate business alerts from detected events"
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Date to process (YYYY-MM-DD format, default: today)"
    )

    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show alert statistics"
    )

    parser.add_argument(
        "--no-save",
        action="store_true",
        help="Don't save alerts to files (display only)"
    )

    args = parser.parse_args()

    if args.stats:
        show_statistics()
    else:
        target_date = None
        if args.date:
            try:
                target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
            except ValueError:
                print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
                return

        run_context_matching(
            target_date=target_date,
            save_alerts=not args.no_save
        )


if __name__ == "__main__":
    main()
