"""
Daily Sales Features Aggregator
Calculates daily aggregations from raw retail sales data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json


class DailyAggregator:
    """
    Aggregates raw sales data into daily features

    Calculates:
    - Daily totals (revenue, units, transactions)
    - By category (revenue, units per department)
    - By location (revenue, traffic per store)
    - Growth rates (vs yesterday, vs last year)
    """

    def __init__(self, sales_df: pd.DataFrame, inventory_df: Optional[pd.DataFrame] = None):
        """
        Initialize aggregator with sales data

        Args:
            sales_df: Raw sales data with columns:
                - Sale Date
                - Sale ID
                - Branch Name
                - Dept Fullname
                - Product
                - Qty Sold
                - Turnover
                - OrderList (supplier)
            inventory_df: Current inventory snapshot
        """
        self.sales_df = sales_df.copy()
        self.inventory_df = inventory_df.copy() if inventory_df is not None else None

        # Ensure Sale Date is datetime (handle different formats)
        self.sales_df['Sale Date'] = pd.to_datetime(self.sales_df['Sale Date'], dayfirst=True, format='mixed')
        self.sales_df['date'] = self.sales_df['Sale Date'].dt.date

        # Cache for performance
        self._cache = {}

    def aggregate_day(self, target_date: datetime.date) -> Dict:
        """
        Calculate all features for a single day

        Args:
            target_date: Date to aggregate

        Returns:
            Dictionary with all daily features
        """
        print(f"Aggregating features for {target_date}...")

        # Filter data for target date
        day_data = self.sales_df[self.sales_df['date'] == target_date]

        if len(day_data) == 0:
            print(f"  ⚠️  No data for {target_date}")
            return None

        features = {
            'date': str(target_date),
            'execution_time': datetime.now().isoformat(),
            'daily_totals': self._calculate_daily_totals(day_data),
            'by_category': self._calculate_by_category(day_data, target_date),
            'by_location': self._calculate_by_location(day_data, target_date),
            'by_supplier': self._calculate_by_supplier(day_data),
            'anomalies': {},  # Will be filled by anomaly detector
        }

        # Add historical context
        features['historical_context'] = self._calculate_historical_context(target_date)

        print(f"  ✓ Aggregated {len(day_data):,} transactions")

        return features

    def _calculate_daily_totals(self, day_data: pd.DataFrame) -> Dict:
        """Calculate overall daily totals"""

        totals = {
            'total_revenue': float(day_data['Turnover'].sum()),
            'total_units': int(day_data['Qty Sold'].sum()),
            'transaction_count': int(day_data['Sale ID'].nunique()),
            'line_items': len(day_data),
            'unique_products': int(day_data['Product'].nunique()),
            'unique_categories': int(day_data['Dept Fullname'].nunique()),
            'avg_ticket': 0.0,
        }

        # Calculate average ticket
        if totals['transaction_count'] > 0:
            totals['avg_ticket'] = round(
                totals['total_revenue'] / totals['transaction_count'], 2
            )

        # Refund metrics (if available)
        if 'Refund Value' in day_data.columns:
            totals['refund_value'] = float(day_data['Refund Value'].sum())
            totals['refund_percentage'] = round(
                (totals['refund_value'] / totals['total_revenue'] * 100)
                if totals['total_revenue'] > 0 else 0, 2
            )

        # Profit metrics (if available)
        if 'Profit' in day_data.columns:
            totals['total_profit'] = float(day_data['Profit'].sum())
            totals['profit_margin'] = round(
                (totals['total_profit'] / totals['total_revenue'] * 100)
                if totals['total_revenue'] > 0 else 0, 2
            )

        return totals

    def _calculate_by_category(self, day_data: pd.DataFrame, target_date: datetime.date) -> Dict:
        """Calculate metrics by department/category"""

        category_stats = {}

        grouped = day_data.groupby('Dept Fullname').agg({
            'Qty Sold': 'sum',
            'Turnover': 'sum',
            'Sale ID': 'nunique',
            'Product': 'nunique',
        }).reset_index()

        for _, row in grouped.iterrows():
            category = row['Dept Fullname']

            category_stats[category] = {
                'revenue': float(row['Turnover']),
                'units': int(row['Qty Sold']),
                'transactions': int(row['Sale ID']),
                'unique_products': int(row['Product']),
                'avg_price_per_unit': round(
                    row['Turnover'] / row['Qty Sold'] if row['Qty Sold'] > 0 else 0, 2
                ),
            }

            # Calculate growth vs yesterday
            yesterday = target_date - timedelta(days=1)
            yesterday_revenue = self._get_category_revenue(category, yesterday)

            if yesterday_revenue > 0:
                growth = ((row['Turnover'] - yesterday_revenue) / yesterday_revenue) * 100
                category_stats[category]['growth_vs_yesterday'] = round(growth, 1)
            else:
                category_stats[category]['growth_vs_yesterday'] = None

            # Calculate growth vs last year
            last_year = target_date.replace(year=target_date.year - 1)
            last_year_revenue = self._get_category_revenue(category, last_year)

            if last_year_revenue > 0:
                growth_yoy = ((row['Turnover'] - last_year_revenue) / last_year_revenue) * 100
                category_stats[category]['growth_vs_last_year'] = round(growth_yoy, 1)
            else:
                category_stats[category]['growth_vs_last_year'] = None

        return category_stats

    def _calculate_by_location(self, day_data: pd.DataFrame, target_date: datetime.date) -> Dict:
        """Calculate metrics by store location"""

        location_stats = {}

        grouped = day_data.groupby('Branch Name').agg({
            'Qty Sold': 'sum',
            'Turnover': 'sum',
            'Sale ID': 'nunique',
        }).reset_index()

        # Calculate network average for comparison
        total_revenue = grouped['Turnover'].sum()
        total_locations = len(grouped)
        network_avg_revenue = total_revenue / total_locations if total_locations > 0 else 0

        for _, row in grouped.iterrows():
            location = row['Branch Name']
            revenue = float(row['Turnover'])

            location_stats[location] = {
                'revenue': revenue,
                'units': int(row['Qty Sold']),
                'traffic': int(row['Sale ID']),  # Transaction count = proxy for foot traffic
                'avg_ticket': round(
                    revenue / row['Sale ID'] if row['Sale ID'] > 0 else 0, 2
                ),
            }

            # Performance vs network average
            if network_avg_revenue > 0:
                vs_avg = ((revenue - network_avg_revenue) / network_avg_revenue) * 100
                location_stats[location]['vs_network_avg'] = round(vs_avg, 1)
            else:
                location_stats[location]['vs_network_avg'] = 0

            # Add inventory if available
            if self.inventory_df is not None:
                location_inventory = self.inventory_df[
                    self.inventory_df['Branch Name'] == location
                ]
                location_stats[location]['current_stock_units'] = int(
                    location_inventory['Branch Stock Level'].sum()
                )

        return location_stats

    def _calculate_by_supplier(self, day_data: pd.DataFrame) -> Dict:
        """Calculate metrics by supplier"""

        supplier_stats = {}

        if 'OrderList' not in day_data.columns:
            return supplier_stats

        grouped = day_data.groupby('OrderList').agg({
            'Turnover': 'sum',
            'Product': 'nunique',
            'Dept Fullname': 'nunique',
        }).reset_index()

        total_revenue = day_data['Turnover'].sum()

        # Only include top suppliers (> 0.5% of daily revenue)
        for _, row in grouped.iterrows():
            supplier = row['OrderList']
            revenue = float(row['Turnover'])

            revenue_pct = (revenue / total_revenue * 100) if total_revenue > 0 else 0

            if revenue_pct > 0.5:  # Only track significant suppliers
                supplier_stats[supplier] = {
                    'revenue': revenue,
                    'revenue_percentage': round(revenue_pct, 2),
                    'product_count': int(row['Product']),
                    'category_count': int(row['Dept Fullname']),
                }

        return supplier_stats

    def _calculate_historical_context(self, target_date: datetime.date) -> Dict:
        """Calculate historical context for comparison"""

        context = {}

        # Same day last year
        last_year = target_date.replace(year=target_date.year - 1)
        last_year_data = self.sales_df[self.sales_df['date'] == last_year]

        if len(last_year_data) > 0:
            last_year_revenue = float(last_year_data['Turnover'].sum())
            context['same_day_last_year'] = {
                'date': str(last_year),
                'revenue': last_year_revenue,
            }

        # 7-day average (trailing)
        seven_days_ago = target_date - timedelta(days=7)
        week_data = self.sales_df[
            (self.sales_df['date'] > seven_days_ago) &
            (self.sales_df['date'] < target_date)
        ]

        if len(week_data) > 0:
            daily_revenues = week_data.groupby('date')['Turnover'].sum()
            context['7_day_average'] = float(daily_revenues.mean())
            context['7_day_median'] = float(daily_revenues.median())

        # 30-day average
        thirty_days_ago = target_date - timedelta(days=30)
        month_data = self.sales_df[
            (self.sales_df['date'] > thirty_days_ago) &
            (self.sales_df['date'] < target_date)
        ]

        if len(month_data) > 0:
            daily_revenues = month_data.groupby('date')['Turnover'].sum()
            context['30_day_average'] = float(daily_revenues.mean())
            context['30_day_median'] = float(daily_revenues.median())

        # Weekday pattern (same weekday over past 8 weeks)
        weekday = target_date.weekday()
        eight_weeks_ago = target_date - timedelta(days=56)
        weekday_data = self.sales_df[
            (self.sales_df['date'] > eight_weeks_ago) &
            (self.sales_df['date'] < target_date) &
            (self.sales_df['Sale Date'].dt.weekday == weekday)
        ]

        if len(weekday_data) > 0:
            daily_revenues = weekday_data.groupby('date')['Turnover'].sum()
            context['weekday_typical'] = float(daily_revenues.median())

        return context

    def _get_category_revenue(self, category: str, date: datetime.date) -> float:
        """Get revenue for a category on a specific date (with caching)"""

        cache_key = f"{category}_{date}"

        if cache_key in self._cache:
            return self._cache[cache_key]

        data = self.sales_df[
            (self.sales_df['date'] == date) &
            (self.sales_df['Dept Fullname'] == category)
        ]

        revenue = float(data['Turnover'].sum()) if len(data) > 0 else 0.0
        self._cache[cache_key] = revenue

        return revenue

    def aggregate_date_range(
        self,
        start_date: datetime.date,
        end_date: datetime.date
    ) -> List[Dict]:
        """
        Aggregate features for a range of dates

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of daily feature dictionaries
        """
        features_list = []

        current_date = start_date
        while current_date <= end_date:
            features = self.aggregate_day(current_date)

            if features is not None:
                features_list.append(features)

            current_date += timedelta(days=1)

        return features_list

    def get_category_baseline(
        self,
        category: str,
        end_date: datetime.date,
        window_days: int = 30
    ) -> Dict:
        """
        Calculate baseline statistics for a category

        Args:
            category: Department name
            end_date: End of baseline period
            window_days: Number of days to include

        Returns:
            Baseline statistics (mean, median, std, percentiles)
        """
        start_date = end_date - timedelta(days=window_days)

        category_data = self.sales_df[
            (self.sales_df['date'] >= start_date) &
            (self.sales_df['date'] <= end_date) &
            (self.sales_df['Dept Fullname'] == category)
        ]

        if len(category_data) == 0:
            return None

        # Daily aggregations
        daily = category_data.groupby('date').agg({
            'Qty Sold': 'sum',
            'Turnover': 'sum',
        })

        baseline = {
            'category': category,
            'window_days': window_days,
            'start_date': str(start_date),
            'end_date': str(end_date),

            # Units
            'daily_avg_units': float(daily['Qty Sold'].mean()),
            'daily_median_units': float(daily['Qty Sold'].median()),
            'daily_std_units': float(daily['Qty Sold'].std()),
            'daily_p25_units': float(daily['Qty Sold'].quantile(0.25)),
            'daily_p75_units': float(daily['Qty Sold'].quantile(0.75)),
            'daily_p95_units': float(daily['Qty Sold'].quantile(0.95)),
            'daily_max_units': float(daily['Qty Sold'].max()),

            # Revenue
            'daily_avg_revenue': float(daily['Turnover'].mean()),
            'daily_median_revenue': float(daily['Turnover'].median()),
            'daily_std_revenue': float(daily['Turnover'].std()),
            'daily_p95_revenue': float(daily['Turnover'].quantile(0.95)),
        }

        return baseline

    def get_location_baseline(
        self,
        location: str,
        end_date: datetime.date,
        window_days: int = 30
    ) -> Dict:
        """
        Calculate baseline statistics for a location

        Args:
            location: Branch name
            end_date: End of baseline period
            window_days: Number of days to include

        Returns:
            Baseline statistics
        """
        start_date = end_date - timedelta(days=window_days)

        location_data = self.sales_df[
            (self.sales_df['date'] >= start_date) &
            (self.sales_df['date'] <= end_date) &
            (self.sales_df['Branch Name'] == location)
        ]

        if len(location_data) == 0:
            return None

        # Daily aggregations
        daily = location_data.groupby('date').agg({
            'Sale ID': 'nunique',
            'Turnover': 'sum',
        })

        baseline = {
            'location': location,
            'window_days': window_days,
            'start_date': str(start_date),
            'end_date': str(end_date),

            # Traffic
            'daily_avg_transactions': float(daily['Sale ID'].mean()),
            'daily_median_transactions': float(daily['Sale ID'].median()),
            'daily_std_transactions': float(daily['Sale ID'].std()),
            'daily_p95_transactions': float(daily['Sale ID'].quantile(0.95)),

            # Revenue
            'daily_avg_revenue': float(daily['Turnover'].mean()),
            'daily_median_revenue': float(daily['Turnover'].median()),
            'daily_std_revenue': float(daily['Turnover'].std()),
        }

        return baseline
