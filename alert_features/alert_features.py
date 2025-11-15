"""
Alert-Specific Feature Calculators
Specialized feature engineering for each alert type
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class AlertFeatureCalculator:
    """
    Calculates specialized features for different alert types
    """

    def __init__(
        self,
        sales_df: pd.DataFrame,
        inventory_df: Optional[pd.DataFrame] = None
    ):
        self.sales_df = sales_df.copy()
        self.inventory_df = inventory_df.copy() if inventory_df is not None else None

        # Ensure date columns (handle different formats)
        self.sales_df['Sale Date'] = pd.to_datetime(self.sales_df['Sale Date'], dayfirst=True, format='mixed')
        self.sales_df['date'] = self.sales_df['Sale Date'].dt.date

    # =========================================================================
    # MAJOR EVENTS Features
    # =========================================================================

    def get_major_event_features(self, location: str, as_of_date: date) -> Dict:
        """
        Calculate features needed for Major Events alert

        For: Concerts, festivals, conferences near locations

        Returns:
            - Location traffic baseline
            - Event-relevant product categories
            - Inventory buffer
            - Peak capacity
        """
        # Calculate traffic baseline (past 30 days)
        thirty_days_ago = as_of_date - timedelta(days=30)

        location_data = self.sales_df[
            (self.sales_df['Branch Name'] == location) &
            (self.sales_df['date'] >= thirty_days_ago) &
            (self.sales_df['date'] <= as_of_date)
        ]

        daily_traffic = location_data.groupby('date')['Sale ID'].nunique()

        features = {
            'location': location,
            'as_of_date': str(as_of_date),

            # Traffic baselines
            'avg_transactions_per_day': float(daily_traffic.mean()),
            'median_transactions_per_day': float(daily_traffic.median()),
            'peak_day_traffic': float(daily_traffic.max()),
            'slowest_day_traffic': float(daily_traffic.min()),
            'std_transactions': float(daily_traffic.std()),

            # Event-relevant categories
            'event_relevant_categories': self._get_event_relevant_categories(
                location, as_of_date
            ),

            # Inventory status
            'inventory_status': self._get_inventory_for_categories(
                location,
                ['OTC : Analgesics', 'OTC : First Aid', 'OTC : Cold & Flu',
                 'Nutritional Supplements', 'Female Toiletries : Hygiene']
            ) if self.inventory_df is not None else {},
        }

        # Historical event impact (if we have past events)
        # This would require event history data - placeholder for now
        features['historical_event_lift'] = 1.8  # Typical 80% lift

        return features

    def _get_event_relevant_categories(self, location: str, as_of_date: date) -> Dict:
        """Get baseline sales for event-relevant categories"""

        categories = [
            'OTC : Analgesics',  # Pain relief
            'OTC : First Aid',  # Plasters, band-aids
            'OTC : Cold & Flu',  # Cough drops, tissues
            'Nutritional Supplements',  # Energy
            'Female Toiletries : Hygiene'  # Travel sizes
        ]

        thirty_days_ago = as_of_date - timedelta(days=30)

        category_stats = {}

        for category in categories:
            cat_data = self.sales_df[
                (self.sales_df['Branch Name'] == location) &
                (self.sales_df['Dept Fullname'] == category) &
                (self.sales_df['date'] >= thirty_days_ago) &
                (self.sales_df['date'] <= as_of_date)
            ]

            if len(cat_data) == 0:
                continue

            daily_revenue = cat_data.groupby('date')['Turnover'].sum()
            daily_units = cat_data.groupby('date')['Qty Sold'].sum()

            category_stats[category] = {
                'baseline_daily_revenue': float(daily_revenue.mean()),
                'baseline_daily_units': float(daily_units.mean()),
                'peak_daily_revenue': float(daily_revenue.max()),
                'peak_daily_units': float(daily_units.max()),
            }

        return category_stats

    def _get_inventory_for_categories(
        self,
        location: str,
        categories: List[str]
    ) -> Dict:
        """Get inventory levels for specific categories at a location"""

        if self.inventory_df is None:
            return {}

        inventory_status = {}

        for category in categories:
            cat_inventory = self.inventory_df[
                (self.inventory_df['Branch Name'] == location) &
                (self.inventory_df['Dept Fullname'] == category)
            ]

            if len(cat_inventory) > 0:
                total_stock = float(cat_inventory['Branch Stock Level'].sum())
                inventory_status[category] = {
                    'stock_units': total_stock,
                    'product_count': int(cat_inventory['Product'].nunique()),
                }

        return inventory_status

    # =========================================================================
    # HEALTH EMERGENCY Features
    # =========================================================================

    def get_health_emergency_features(
        self,
        category: str,
        as_of_date: date
    ) -> Dict:
        """
        Calculate features for Health Emergency alerts

        For: Flu outbreak, norovirus, food poisoning

        Returns:
            - Category demand baseline
            - Seasonal peak patterns
            - Current inventory vs spike requirements
            - Days of supply calculations
        """
        # Get full year of data for seasonality
        one_year_ago = as_of_date.replace(year=as_of_date.year - 1)

        category_data = self.sales_df[
            (self.sales_df['Dept Fullname'] == category) &
            (self.sales_df['date'] >= one_year_ago) &
            (self.sales_df['date'] <= as_of_date)
        ]

        if len(category_data) == 0:
            return None

        # Daily aggregations
        daily = category_data.groupby('date').agg({
            'Qty Sold': 'sum',
            'Turnover': 'sum',
        })

        # Recent 30-day baseline
        thirty_days_ago = as_of_date - timedelta(days=30)
        recent_data = daily[daily.index >= thirty_days_ago]

        # Monthly patterns (for seasonality)
        category_data['month'] = pd.to_datetime(category_data['Sale Date']).dt.month
        monthly = category_data.groupby('month').agg({
            'Qty Sold': 'sum',
            'Turnover': 'sum',
        })

        # Calculate days in each month for proper averaging
        days_per_month = category_data.groupby('month')['date'].nunique()
        monthly['avg_daily_units'] = monthly['Qty Sold'] / days_per_month
        monthly['avg_daily_revenue'] = monthly['Turnover'] / days_per_month

        peak_month = monthly['avg_daily_units'].idxmax()
        peak_daily_units = float(monthly.loc[peak_month, 'avg_daily_units'])

        features = {
            'category': category,
            'as_of_date': str(as_of_date),

            # Current baseline (30 days)
            'daily_avg_units': float(recent_data['Qty Sold'].mean()),
            'daily_avg_revenue': float(recent_data['Turnover'].mean()),
            'daily_median_units': float(recent_data['Qty Sold'].median()),
            'daily_std_units': float(recent_data['Qty Sold'].std()),

            # Historical peaks
            'historical_peak_daily_units': float(daily['Qty Sold'].max()),
            'historical_peak_daily_revenue': float(daily['Turnover'].max()),
            'peak_month': int(peak_month),
            'peak_month_avg_daily_units': peak_daily_units,

            # Emergency spike estimates (4-5x normal)
            'outbreak_estimated_peak_units': float(recent_data['Qty Sold'].mean() * 4.5),
            'outbreak_estimated_peak_revenue': float(recent_data['Turnover'].mean() * 4.5),
        }

        # Add inventory health if available
        if self.inventory_df is not None:
            inventory_health = self._calculate_inventory_health(
                category,
                features['daily_avg_units'],
                features['outbreak_estimated_peak_units']
            )
            features['inventory_health'] = inventory_health

        # Supplier information
        features['suppliers'] = self._get_category_suppliers(category)

        return features

    def _calculate_inventory_health(
        self,
        category: str,
        normal_daily_units: float,
        spike_daily_units: float
    ) -> Dict:
        """Calculate inventory adequacy for a category"""

        if self.inventory_df is None:
            return {}

        category_inventory = self.inventory_df[
            self.inventory_df['Dept Fullname'] == category
        ]

        total_stock = float(category_inventory['Branch Stock Level'].sum())

        health = {
            'total_current_stock': total_stock,
            'normal_daily_consumption': normal_daily_units,
            'spike_daily_consumption': spike_daily_units,
        }

        if normal_daily_units > 0:
            health['days_of_supply_normal'] = round(total_stock / normal_daily_units, 1)
        else:
            health['days_of_supply_normal'] = None

        if spike_daily_units > 0:
            health['days_of_supply_outbreak'] = round(total_stock / spike_daily_units, 1)
            health['alert_needed'] = health['days_of_supply_outbreak'] < 5  # Less than 5 days = alert
        else:
            health['days_of_supply_outbreak'] = None
            health['alert_needed'] = False

        # By location breakdown
        health['by_location'] = {}
        for _, row in category_inventory.iterrows():
            location = row['Branch Name']
            stock = float(row['Branch Stock Level'])

            health['by_location'][location] = {
                'stock': stock,
                'days_normal': round(stock / normal_daily_units, 1) if normal_daily_units > 0 else None,
                'days_spike': round(stock / spike_daily_units, 1) if spike_daily_units > 0 else None,
            }

        return health

    def _get_category_suppliers(self, category: str) -> List[Dict]:
        """Get list of suppliers for a category"""

        if 'OrderList' not in self.sales_df.columns:
            return []

        category_data = self.sales_df[
            self.sales_df['Dept Fullname'] == category
        ]

        supplier_stats = category_data.groupby('OrderList').agg({
            'Turnover': 'sum',
            'Product': 'nunique',
        }).reset_index()

        total_category_revenue = category_data['Turnover'].sum()

        suppliers = []
        for _, row in supplier_stats.iterrows():
            revenue_pct = (row['Turnover'] / total_category_revenue * 100) if total_category_revenue > 0 else 0

            suppliers.append({
                'supplier': row['OrderList'],
                'revenue_percentage': round(revenue_pct, 1),
                'product_count': int(row['Product']),
                # Lead time would come from supplier master data
                'typical_lead_time_days': 3,  # Placeholder
            })

        # Sort by revenue percentage
        suppliers.sort(key=lambda x: x['revenue_percentage'], reverse=True)

        return suppliers

    # =========================================================================
    # WEATHER EXTREME Features
    # =========================================================================

    def get_weather_features(
        self,
        weather_type: str,
        as_of_date: date
    ) -> Dict:
        """
        Calculate features for Weather Extreme alerts

        Args:
            weather_type: 'heatwave', 'cold_snap', 'flooding'
            as_of_date: Date to calculate features as of

        Returns:
            Seasonal patterns and inventory for weather-sensitive categories
        """
        # Map weather to categories
        weather_category_map = {
            'heatwave': ['Skincare', 'OTC : Allergy', 'Nutritional Supplements'],
            'cold_snap': ['OTC : Cold & Flu', 'Vitamins'],
            'flooding': ['OTC : First Aid', 'Female Toiletries : Hygiene'],
        }

        categories = weather_category_map.get(weather_type, [])

        if not categories:
            return None

        features = {
            'weather_type': weather_type,
            'as_of_date': str(as_of_date),
            'relevant_categories': categories,
            'category_patterns': {},
        }

        # Get seasonal patterns for each category
        for category in categories:
            pattern = self._get_seasonal_pattern(category, as_of_date)
            if pattern:
                features['category_patterns'][category] = pattern

        return features

    def _get_seasonal_pattern(self, category: str, as_of_date: date) -> Dict:
        """Get seasonal sales pattern for a category"""

        # Get 24 months of data for good seasonality
        two_years_ago = as_of_date.replace(year=as_of_date.year - 2)

        category_data = self.sales_df[
            (self.sales_df['Dept Fullname'] == category) &
            (self.sales_df['date'] >= two_years_ago) &
            (self.sales_df['date'] <= as_of_date)
        ]

        if len(category_data) == 0:
            return None

        # Monthly aggregations
        category_data['month'] = pd.to_datetime(category_data['Sale Date']).dt.month

        monthly = category_data.groupby('month').agg({
            'date': 'nunique',  # Days in month
            'Qty Sold': 'sum',
            'Turnover': 'sum',
        }).reset_index()

        monthly['daily_units'] = monthly['Qty Sold'] / monthly['date']
        monthly['daily_revenue'] = monthly['Turnover'] / monthly['date']

        # Convert to dict by month
        seasonal_baseline = {}
        for _, row in monthly.iterrows():
            month = int(row['month'])
            month_name = datetime(2000, month, 1).strftime('%b')

            seasonal_baseline[month_name] = {
                'daily_units': round(row['daily_units'], 1),
                'daily_revenue': round(row['daily_revenue'], 2),
            }

        # Identify peaks
        peak_month_idx = monthly['daily_units'].idxmax()
        peak_month = int(monthly.loc[peak_month_idx, 'month'])

        pattern = {
            'seasonal_baseline': seasonal_baseline,
            'peak_month': datetime(2000, peak_month, 1).strftime('%b'),
            'peak_daily_units': float(monthly.loc[peak_month_idx, 'daily_units']),
            'peak_daily_revenue': float(monthly.loc[peak_month_idx, 'daily_revenue']),
        }

        # Current month baseline
        current_month = as_of_date.month
        current_month_data = monthly[monthly['month'] == current_month]

        if len(current_month_data) > 0:
            pattern['current_month_baseline'] = {
                'daily_units': float(current_month_data.iloc[0]['daily_units']),
                'daily_revenue': float(current_month_data.iloc[0]['daily_revenue']),
            }

        # Add inventory if available
        if self.inventory_df is not None:
            cat_inventory = self.inventory_df[
                self.inventory_df['Dept Fullname'] == category
            ]
            pattern['current_stock'] = float(cat_inventory['Branch Stock Level'].sum())

            if 'current_month_baseline' in pattern:
                normal_daily = pattern['current_month_baseline']['daily_units']
                peak_daily = pattern['peak_daily_units']

                if normal_daily > 0:
                    pattern['days_of_supply_normal'] = round(pattern['current_stock'] / normal_daily, 1)

                if peak_daily > 0:
                    pattern['days_of_supply_peak'] = round(pattern['current_stock'] / peak_daily, 1)

        return pattern

    # =========================================================================
    # SUPPLY DISRUPTION Features
    # =========================================================================

    def get_supply_disruption_features(self, as_of_date: date) -> Dict:
        """
        Calculate features for Supply Disruption alerts

        Returns:
            - Supplier criticality rankings
            - Product dependencies
            - Days of supply by supplier
        """
        if 'OrderList' not in self.sales_df.columns:
            return None

        # Get past 12 months
        one_year_ago = as_of_date.replace(year=as_of_date.year - 1)

        sales_data = self.sales_df[
            (self.sales_df['date'] >= one_year_ago) &
            (self.sales_df['date'] <= as_of_date)
        ]

        # Supplier criticality
        supplier_stats = sales_data.groupby('OrderList').agg({
            'Turnover': 'sum',
            'Product': 'nunique',
            'Dept Fullname': 'nunique',
        }).reset_index()

        total_revenue = sales_data['Turnover'].sum()

        supplier_criticality = {}

        for _, row in supplier_stats.iterrows():
            supplier = row['OrderList']
            revenue = row['Turnover']
            revenue_pct = (revenue / total_revenue) if total_revenue > 0 else 0

            # Only track suppliers > 1% of revenue
            if revenue_pct < 0.01:
                continue

            # Criticality score
            if revenue_pct > 0.15:
                criticality = "CRITICAL"
            elif revenue_pct > 0.05:
                criticality = "HIGH"
            elif revenue_pct > 0.02:
                criticality = "MEDIUM"
            else:
                criticality = "LOW"

            supplier_criticality[supplier] = {
                'revenue_dependency': round(revenue_pct, 4),
                'product_count': int(row['Product']),
                'category_count': int(row['Dept Fullname']),
                'monthly_spend_estimate': round(revenue / 12, 2),
                'criticality_rank': criticality,
            }

        features = {
            'as_of_date': str(as_of_date),
            'supplier_criticality': supplier_criticality,
        }

        # If we have inventory, calculate days of supply by supplier
        if self.inventory_df is not None:
            features['supply_chain_resilience'] = self._calculate_supplier_resilience(
                sales_data, as_of_date
            )

        return features

    def _calculate_supplier_resilience(
        self,
        sales_data: pd.DataFrame,
        as_of_date: date
    ) -> Dict:
        """Calculate resilience metrics for each supplier"""

        resilience = {}

        # Calculate daily sales rate (last 30 days)
        thirty_days_ago = as_of_date - timedelta(days=30)
        recent_sales = sales_data[sales_data['date'] >= thirty_days_ago]

        product_daily_sales = recent_sales.groupby(['Product', 'OrderList']).agg({
            'Qty Sold': 'sum',
            'date': 'nunique',
        }).reset_index()

        product_daily_sales['daily_sales'] = product_daily_sales['Qty Sold'] / product_daily_sales['date']

        # Join with inventory
        if self.inventory_df is not None:
            # Aggregate inventory by product
            inventory_by_product = self.inventory_df.groupby('Product').agg({
                'Branch Stock Level': 'sum',
            }).reset_index()

            # Merge
            product_info = product_daily_sales.merge(
                inventory_by_product,
                on='Product',
                how='left'
            )

            product_info['Branch Stock Level'] = product_info['Branch Stock Level'].fillna(0)
            product_info['days_of_supply'] = product_info['Branch Stock Level'] / product_info['daily_sales']

            # Group by supplier
            for supplier in product_info['OrderList'].unique():
                supplier_products = product_info[product_info['OrderList'] == supplier]

                # Get critical products (low days of supply)
                critical = supplier_products.nsmallest(5, 'days_of_supply')

                resilience[supplier] = {
                    'total_products': len(supplier_products),
                    'avg_days_of_supply': float(supplier_products['days_of_supply'].mean()),
                    'min_days_of_supply': float(supplier_products['days_of_supply'].min()),
                    'critical_products': [
                        {
                            'product': row['Product'],
                            'current_stock': float(row['Branch Stock Level']),
                            'daily_sales': round(row['daily_sales'], 2),
                            'days_of_supply': round(row['days_of_supply'], 1),
                        }
                        for _, row in critical.iterrows()
                    ],
                }

        return resilience

    # =========================================================================
    # VIRAL TREND Features
    # =========================================================================

    def get_viral_trend_features(
        self,
        product_keyword: str,
        as_of_date: date
    ) -> Dict:
        """
        Calculate features for Viral Trend alerts

        Args:
            product_keyword: Keyword to search for trending products
            as_of_date: Date to calculate features

        Returns:
            Product availability, stock levels, sales rates
        """
        # Search for products matching keyword
        matching_products = self.sales_df[
            self.sales_df['Product'].str.contains(product_keyword, case=False, na=False)
        ]

        if len(matching_products) == 0:
            return {'found': False, 'keyword': product_keyword}

        # Get unique products
        products = matching_products['Product'].unique()

        # Calculate sales rate (last 30 days)
        thirty_days_ago = as_of_date - timedelta(days=30)

        recent_sales = matching_products[
            (matching_products['date'] >= thirty_days_ago) &
            (matching_products['date'] <= as_of_date)
        ]

        product_stats = recent_sales.groupby('Product').agg({
            'date': 'nunique',
            'Qty Sold': 'sum',
            'Turnover': 'sum',
        }).reset_index()

        product_stats['daily_sales_normal'] = product_stats['Qty Sold'] / product_stats['date']
        product_stats['daily_revenue_normal'] = product_stats['Turnover'] / product_stats['date']

        features = {
            'found': True,
            'keyword': product_keyword,
            'as_of_date': str(as_of_date),
            'matching_products_count': len(products),
            'products': [],
        }

        for _, row in product_stats.iterrows():
            product = row['Product']

            product_info = {
                'product': product,
                'daily_sales_normal': round(row['daily_sales_normal'], 2),
                'daily_revenue_normal': round(row['daily_revenue_normal'], 2),
            }

            # Add inventory if available
            if self.inventory_df is not None:
                product_inventory = self.inventory_df[
                    self.inventory_df['Product'] == product
                ]

                total_stock = float(product_inventory['Branch Stock Level'].sum())
                product_info['current_stock'] = total_stock

                if row['daily_sales_normal'] > 0:
                    product_info['days_of_supply'] = round(
                        total_stock / row['daily_sales_normal'], 1
                    )

                    # Viral spike estimate (3-5x normal)
                    viral_daily_sales = row['daily_sales_normal'] * 4.0
                    product_info['days_of_supply_at_4x_spike'] = round(
                        total_stock / viral_daily_sales, 1
                    )

                    product_info['can_capitalize'] = product_info['days_of_supply_at_4x_spike'] > 3

                # By location
                product_info['stocked_in_locations'] = int(len(product_inventory))
                product_info['locations'] = product_inventory['Branch Name'].tolist()

            features['products'].append(product_info)

        return features
