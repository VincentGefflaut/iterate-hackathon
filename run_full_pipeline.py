#!/usr/bin/env python3
"""
Full News Alerts Pipeline - End-to-end execution for a specific date

Orchestrates the complete pipeline:
1. Build alert features (data engineering)
2. Fetch news articles
3. Detect events (Agent 1)
4. Match to business context (Agent 2)
5. Generate actionable alerts

Usage:
    # Run full pipeline for today
    python run_full_pipeline.py

    # Run for specific date
    python run_full_pipeline.py --date 2024-11-15

    # Use real data for context matching
    python run_full_pipeline.py --date 2024-11-15 --use-real-data

    # Demo mode (no API calls, uses mock data)
    python run_full_pipeline.py --demo

    # Skip LLM enhancements (faster, cheaper)
    python run_full_pipeline.py --date 2024-11-15 --no-llm
"""

import argparse
import sys
import subprocess
from datetime import date, datetime, timedelta
from pathlib import Path
import json


def print_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_step(step_num, total_steps, description):
    """Print a step indicator"""
    print(f"\n{'─' * 80}")
    print(f"STEP {step_num}/{total_steps}: {description}")
    print('─' * 80)


def run_command(cmd, description, required=True):
    """
    Run a shell command and handle errors

    Args:
        cmd: Command as list of strings
        description: Human-readable description
        required: If True, exit on failure. If False, continue

    Returns:
        True if successful, False otherwise
    """
    print(f"\n▶ {description}...")
    print(f"  Command: {' '.join(cmd)}\n")

    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✅ {description} - SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {description} - FAILED")
        print(f"   Exit code: {e.returncode}")

        if required:
            print("\n⚠️  This step is required. Pipeline cannot continue.")
            sys.exit(1)
        else:
            print("\n⚠️  This step failed but is not critical. Continuing...")
            return False
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")
        if required:
            sys.exit(1)
        return False


def check_data_files():
    """Check if required data files exist"""
    sales_file = Path("data/input/Retail/retail_sales_data_01_09_2023_to_31_10_2025.csv")
    inventory_file = Path("data/input/Retail/retail_inventory_snapshot_30_10_25.csv")

    has_sales = sales_file.exists()
    has_inventory = inventory_file.exists()

    if has_sales and has_inventory:
        return "available"
    elif has_sales or has_inventory:
        return "partial"
    else:
        return "missing"


def run_full_pipeline(
    target_date: date,
    use_real_data: bool = False,
    enhance_with_llm: bool = True,
    demo_mode: bool = False,
    skip_features: bool = False
):
    """
    Run the complete news alerts pipeline

    Args:
        target_date: Date to process
        use_real_data: Whether to use real business data for context matching
        enhance_with_llm: Whether to use LLM enhancements
        demo_mode: Whether to run in demo mode (no real API calls)
        skip_features: Skip feature building (faster for testing)
    """

    print_header("NEWS ALERTS PIPELINE - FULL EXECUTION")

    print(f"📅 Target Date: {target_date.isoformat()}")
    print(f"🔧 Mode: {'DEMO' if demo_mode else 'PRODUCTION'}")
    print(f"📊 Data: {'Real Business Data' if use_real_data else 'Heuristic-Based'}")
    print(f"🤖 LLM: {'Enabled' if enhance_with_llm else 'Disabled'}")
    print()

    total_steps = 4 if not skip_features else 3
    current_step = 0

    # STEP 1: Build Alert Features (if not skipping and data available)
    if not skip_features and use_real_data:
        current_step += 1
        print_step(current_step, total_steps, "Build Alert Features (Data Engineering)")

        data_status = check_data_files()

        if data_status == "available":
            # Build features for the target date
            run_command(
                ["python", "build_alert_features.py", "--date", target_date.isoformat()],
                "Building alert features for target date",
                required=False  # Not critical - will fall back to heuristics
            )
        elif data_status == "partial":
            print("⚠️  Some data files missing. Skipping feature building.")
            print("   Context matching will use heuristic mode.")
        else:
            print("⚠️  Data files not found. Skipping feature building.")
            print("   Place CSV files in data/input/Retail/ to enable data-driven mode.")
            use_real_data = False  # Force heuristic mode
    elif skip_features:
        print("\n⏭️  Skipping feature building (--skip-features flag)")
    elif not use_real_data:
        print("\n⏭️  Skipping feature building (heuristic mode, no data needed)")

    # STEP 2: Fetch News & Detect Events (Agent 1)
    current_step += 1
    print_step(current_step, total_steps, "Fetch News & Detect Events (Agent 1)")

    if demo_mode:
        # Demo mode - use mock events
        run_command(
            ["python", "run_news_alerts.py", "--demo"],
            "Running event detector in DEMO mode",
            required=True
        )
    else:
        # Production mode - fetch real news
        run_command(
            ["python", "run_news_alerts.py", "--max-articles", "50"],
            "Fetching news and detecting events (limited to 50 articles)",
            required=True
        )

    # STEP 3: Context Matching (Agent 2)
    current_step += 1
    print_step(current_step, total_steps, "Context Matching (Agent 2)")

    # Build context matcher command
    context_cmd = ["python", "run_context_matcher.py", "--date", target_date.isoformat()]

    if use_real_data:
        context_cmd.append("--use-real-data")

    if not enhance_with_llm:
        context_cmd.append("--no-llm")

    run_command(
        context_cmd,
        "Matching events to business context and generating alerts",
        required=True
    )

    # STEP 4: Summary
    current_step += 1
    print_step(current_step, total_steps, "Pipeline Summary")

    # Check output files
    events_file = Path(f"data/events/events_{target_date.isoformat()}.json")
    alerts_dir = Path("data/alerts")
    report_file = alerts_dir / f"daily_report_{target_date.isoformat()}.json"

    print("\n📁 Output Files:")
    print(f"   Events: {events_file}")
    print(f"   Alerts: {alerts_dir}/")
    print(f"   Report: {report_file}")
    print()

    # Load and display summary
    if report_file.exists():
        with open(report_file, 'r') as f:
            report = json.load(f)

        print("📊 PIPELINE RESULTS:")
        print(f"   Events detected: {report.get('total_events_evaluated', 0)}")
        print(f"   Alerts generated: {report.get('alerts_generated', 0)}")
        print()

        if report.get('alerts_by_severity'):
            print("   Alerts by severity:")
            for severity, count in sorted(report['alerts_by_severity'].items()):
                emoji = "🚨" if severity == "critical" else "⚠️" if severity == "high" else "ℹ️"
                print(f"     {emoji} {severity}: {count}")

        print()

        if report.get('recommended_priorities'):
            print("   Top priorities:")
            for i, priority in enumerate(report['recommended_priorities'][:3], 1):
                print(f"     {i}. {priority}")

        print()
        print(f"📄 View full report: cat {report_file}")

    print_header("✅ PIPELINE COMPLETE")

    print("Next steps:")
    print(f"  • Review alerts: python run_context_matcher.py --stats")
    print(f"  • View report: cat {report_file}")
    print(f"  • Test integration: python test_data_integration.py")
    print()


def run_demo_pipeline():
    """Run a quick demo pipeline with mock data"""
    print_header("DEMO MODE - Quick Pipeline Test")

    print("This will run the pipeline with mock/demo data (no API calls):\n")
    print("  ✓ No API keys required")
    print("  ✓ No data files required")
    print("  ✓ Fast execution (~5 seconds)")
    print("  ✓ Shows example outputs")
    print()

    # Create demo events directly using test script
    print_step(1, 2, "Creating Demo Events")
    run_command(
        ["python", "test_data_integration.py"],
        "Creating mock events for testing",
        required=False
    )

    # Save a demo event for context matcher to use
    print("\n▶ Generating demo event file...")
    from news_alerts.models import DetectedEvent
    from news_alerts.event_storage import EventStorage
    from datetime import date

    demo_event = DetectedEvent(
        event_type="health_emergency",
        title="Norovirus Outbreak in Dublin (DEMO)",
        description="Health officials report increased norovirus cases. This is a DEMO event.",
        severity="high",
        urgency="immediate",
        location="Dublin, Ireland",
        confidence="high",
        event_date=date.today().isoformat(),
        published_at=date.today().isoformat() + "T10:00:00Z",
        source_url="https://demo.example.com/norovirus",
        key_facts=["DEMO event", "For testing purposes"],
        potential_relevance="Demo event to test pipeline"
    )

    storage = EventStorage()
    storage.save_event(demo_event)
    print("✅ Demo event created")

    # Run context matcher
    print_step(2, 2, "Context Matching (Demo)")
    run_command(
        ["python", "run_context_matcher.py", "--date", date.today().isoformat(), "--no-llm"],
        "Matching demo events to business context",
        required=True
    )

    print_header("✅ DEMO COMPLETE")
    print("\nThis was a quick demo. For production use:")
    print("  python run_full_pipeline.py --date 2024-11-15 --use-real-data")


def main():
    parser = argparse.ArgumentParser(
        description="Run the full news alerts pipeline for a specific date",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline for today
  python run_full_pipeline.py

  # Run for specific date with real data
  python run_full_pipeline.py --date 2024-11-15 --use-real-data

  # Demo mode (no API calls)
  python run_full_pipeline.py --demo

  # Production mode, no LLM (faster)
  python run_full_pipeline.py --date 2024-11-15 --no-llm

  # Skip feature building (faster for testing)
  python run_full_pipeline.py --skip-features
"""
    )

    parser.add_argument(
        "--date",
        type=str,
        help="Date to process (YYYY-MM-DD format, default: today)"
    )

    parser.add_argument(
        "--use-real-data",
        action="store_true",
        help="Use real sales/inventory data for context matching (requires data files)"
    )

    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Disable LLM enhancements (faster, cheaper)"
    )

    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with mock data (no API calls)"
    )

    parser.add_argument(
        "--skip-features",
        action="store_true",
        help="Skip feature building step (faster for testing)"
    )

    args = parser.parse_args()

    # Parse target date
    if args.date:
        try:
            target_date = datetime.strptime(args.date, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD")
            sys.exit(1)
    else:
        target_date = date.today()

    # Run pipeline
    if args.demo:
        run_demo_pipeline()
    else:
        run_full_pipeline(
            target_date=target_date,
            use_real_data=args.use_real_data,
            enhance_with_llm=not args.no_llm,
            demo_mode=False,
            skip_features=args.skip_features
        )


if __name__ == "__main__":
    main()
