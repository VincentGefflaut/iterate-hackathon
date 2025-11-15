"""
Build Alert Features Pipeline
Main script to generate daily features for alert system

Usage:
    # Build features for yesterday
    python build_alert_features.py

    # Build features for specific date
    python build_alert_features.py --date 2024-10-15

    # Build features for date range
    python build_alert_features.py --start 2024-10-01 --end 2024-10-31

    # Show cache stats
    python build_alert_features.py --stats
"""

import pandas as pd
import argparse
from datetime import datetime, date, timedelta
from pathlib import Path

from alert_features import (
    DailyAggregator,
    AlertFeatureCalculator,
    AnomalyDetector,
    FeatureCache
)


def load_data():
    """Load sales and inventory data"""
    print("Loading data...")

    # Load sales data
    sales_file = "data/input/Retail/retail_sales_data_01_09_2023_to_31_10_2025.csv"
    sales_df = pd.read_csv(sales_file, encoding='utf-8-sig', low_memory=False)
    print(f"  ✓ Loaded {len(sales_df):,} sales records")

    # Load inventory data
    inventory_file = "data/input/Retail/retail_inventory_snapshot_30_10_25.csv"
    inventory_df = pd.read_csv(inventory_file, encoding='utf-8-sig', low_memory=False)
    print(f"  ✓ Loaded {len(inventory_df):,} inventory records")

    return sales_df, inventory_df


def build_baselines(sales_df: pd.DataFrame, as_of_date: date) -> dict:
    """Build baseline statistics"""
    print("\nCalculating baselines...")

    detector = AnomalyDetector(baseline_window_days=30)
    baselines = detector.calculate_baselines(sales_df, as_of_date, window_days=30)

    print(f"  ✓ Calculated baselines for {len(baselines.get('by_category', {}))} categories")
    print(f"  ✓ Calculated baselines for {len(baselines.get('by_location', {}))} locations")

    return baselines


def build_daily_features(
    sales_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    target_date: date,
    baselines: dict
) -> dict:
    """Build features for a single day"""

    # Daily aggregation
    aggregator = DailyAggregator(sales_df, inventory_df)
    features = aggregator.aggregate_day(target_date)

    if features is None:
        return None

    # Anomaly detection
    detector = AnomalyDetector()
    anomalies = detector.detect_daily_anomalies(features, baselines)
    features['anomalies'] = anomalies

    # Print anomaly report if any found
    if anomalies['has_anomaly']:
        print("\n" + detector.generate_anomaly_report(anomalies))

    return features


def build_date_range(
    sales_df: pd.DataFrame,
    inventory_df: pd.DataFrame,
    start_date: date,
    end_date: date,
    cache: FeatureCache
):
    """Build features for a date range"""
    print(f"\nBuilding features from {start_date} to {end_date}...")

    # Calculate baselines using data up to start_date
    baselines = build_baselines(sales_df, start_date)
    cache.save_baselines(baselines)

    # Build features for each day
    current_date = start_date
    success_count = 0

    while current_date <= end_date:
        # Check if already cached
        if cache.has_features(current_date):
            print(f"  ⏭️  {current_date} - already cached")
            current_date += timedelta(days=1)
            continue

        # Build features
        features = build_daily_features(sales_df, inventory_df, current_date, baselines)

        if features:
            cache.save_daily_features(features, current_date)
            success_count += 1
        else:
            print(f"  ⚠️  {current_date} - no data")

        current_date += timedelta(days=1)

    print(f"\n✅ Successfully built features for {success_count} days")


def show_demo_features(cache: FeatureCache):
    """Show example alert-specific features"""
    print("\n" + "=" * 80)
    print("DEMO: Alert-Specific Features")
    print("=" * 80)

    # Load latest date
    latest_date = cache.get_latest_cached_date()

    if not latest_date:
        print("No cached features available. Run with --build first.")
        return

    print(f"\nUsing features from: {latest_date}")

    # Load data
    sales_df, inventory_df = load_data()

    # Create calculator
    calc = AlertFeatureCalculator(sales_df, inventory_df)

    # 1. Major Events features
    print("\n" + "-" * 80)
    print("1. MAJOR EVENTS Features (for Baggot St)")
    print("-" * 80)

    major_event = calc.get_major_event_features("Baggot St", latest_date)

    if major_event:
        print(f"\nTraffic Baseline:")
        print(f"  Avg daily transactions: {major_event['avg_transactions_per_day']:.0f}")
        print(f"  Peak day: {major_event['peak_day_traffic']:.0f}")
        print(f"  Slowest day: {major_event['slowest_day_traffic']:.0f}")

        print(f"\nEvent-relevant categories:")
        for cat, stats in list(major_event['event_relevant_categories'].items())[:3]:
            print(f"  {cat}:")
            print(f"    Daily baseline: €{stats['baseline_daily_revenue']:.2f} ({stats['baseline_daily_units']:.1f} units)")

    # 2. Health Emergency features
    print("\n" + "-" * 80)
    print("2. HEALTH EMERGENCY Features (OTC : Cold & Flu)")
    print("-" * 80)

    health = calc.get_health_emergency_features("OTC : Cold & Flu", latest_date)

    if health:
        print(f"\nDemand Baseline:")
        print(f"  Daily avg: {health['daily_avg_units']:.1f} units (€{health['daily_avg_revenue']:.2f})")
        print(f"  Historical peak: {health['historical_peak_daily_units']:.0f} units")
        print(f"  Outbreak estimate: {health['outbreak_estimated_peak_units']:.0f} units")

        if health.get('inventory_health'):
            inv = health['inventory_health']
            print(f"\nInventory Health:")
            print(f"  Current stock: {inv['total_current_stock']:.0f} units")
            print(f"  Days of supply (normal): {inv.get('days_of_supply_normal', 'N/A')}")
            print(f"  Days of supply (outbreak): {inv.get('days_of_supply_outbreak', 'N/A')}")
            print(f"  ALERT NEEDED: {inv.get('alert_needed', False)}")

        if health.get('suppliers'):
            print(f"\nTop Suppliers:")
            for sup in health['suppliers'][:3]:
                print(f"  {sup['supplier']}: {sup['revenue_percentage']:.1f}% of category")

    # 3. Weather features
    print("\n" + "-" * 80)
    print("3. WEATHER Features (Heatwave)")
    print("-" * 80)

    weather = calc.get_weather_features("heatwave", latest_date)

    if weather and weather.get('category_patterns'):
        for cat, pattern in list(weather['category_patterns'].items())[:2]:
            print(f"\n{cat}:")

            if pattern.get('seasonal_baseline'):
                print(f"  Seasonal pattern:")
                for month in ['Jan', 'Jun', 'Jul', 'Aug']:
                    if month in pattern['seasonal_baseline']:
                        data = pattern['seasonal_baseline'][month]
                        print(f"    {month}: {data['daily_units']:.0f} units/day (€{data['daily_revenue']:.0f})")

            if pattern.get('current_stock'):
                print(f"  Current stock: {pattern['current_stock']:.0f} units")
                if pattern.get('days_of_supply_peak'):
                    print(f"  Days of supply (peak): {pattern['days_of_supply_peak']:.1f} days")

    # 4. Supply Disruption features
    print("\n" + "-" * 80)
    print("4. SUPPLY DISRUPTION Features")
    print("-" * 80)

    supply = calc.get_supply_disruption_features(latest_date)

    if supply and supply.get('supplier_criticality'):
        print(f"\nTop Critical Suppliers:")
        sorted_suppliers = sorted(
            supply['supplier_criticality'].items(),
            key=lambda x: x[1]['revenue_dependency'],
            reverse=True
        )

        for supplier, stats in sorted_suppliers[:5]:
            print(f"\n  {supplier}:")
            print(f"    Revenue dependency: {stats['revenue_dependency']*100:.1f}%")
            print(f"    Product count: {stats['product_count']}")
            print(f"    Criticality: {stats['criticality_rank']}")

    # 5. Viral Trend features
    print("\n" + "-" * 80)
    print("5. VIRAL TREND Features (Weight loss products)")
    print("-" * 80)

    viral = calc.get_viral_trend_features("weight", latest_date)

    if viral.get('found'):
        print(f"\nFound {viral['matching_products_count']} matching products")

        for prod in viral['products'][:3]:
            print(f"\n  {prod['product']}:")
            print(f"    Daily sales (normal): {prod['daily_sales_normal']:.2f} units")
            if prod.get('current_stock'):
                print(f"    Current stock: {prod['current_stock']:.0f} units")
                print(f"    Days of supply: {prod.get('days_of_supply', 'N/A')}")
                print(f"    Can capitalize (4x spike): {prod.get('can_capitalize', 'N/A')}")

    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Build alert features")

    parser.add_argument('--date', type=str, help='Single date to process (YYYY-MM-DD)')
    parser.add_argument('--start', type=str, help='Start date for range (YYYY-MM-DD)')
    parser.add_argument('--end', type=str, help='End date for range (YYYY-MM-DD)')
    parser.add_argument('--stats', action='store_true', help='Show cache statistics')
    parser.add_argument('--demo', action='store_true', help='Show demo of alert features')
    parser.add_argument('--export', type=str, help='Export cached features to CSV')
    parser.add_argument('--clean', action='store_true', help='Delete old cache files (>90 days)')

    args = parser.parse_args()

    # Initialize cache
    cache = FeatureCache()

    # Show stats
    if args.stats:
        cache.print_cache_stats()
        return

    # Show demo
    if args.demo:
        show_demo_features(cache)
        return

    # Export
    if args.export:
        cache.export_to_csv(args.export)
        print(f"\n✅ Exported to {args.export}")
        return

    # Clean old cache
    if args.clean:
        deleted = cache.delete_old_cache(keep_days=90)
        print(f"\n✅ Cleaned up cache ({deleted} files deleted)")
        return

    # Load data
    sales_df, inventory_df = load_data()

    # Determine date range
    if args.date:
        # Single date
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
        end_date = target_date
    elif args.start and args.end:
        # Date range
        target_date = datetime.strptime(args.start, '%Y-%m-%d').date()
        end_date = datetime.strptime(args.end, '%Y-%m-%d').date()
    else:
        # Default: yesterday
        target_date = date.today() - timedelta(days=1)
        end_date = target_date

    # Build features
    build_date_range(sales_df, inventory_df, target_date, end_date, cache)

    # Show stats
    print()
    cache.print_cache_stats()


if __name__ == "__main__":
    main()
