"""
Anomaly Detection System
Detects unusual patterns in sales data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Literal
from scipy import stats


class AnomalyDetector:
    """
    Detects anomalies in sales data using statistical methods

    Uses z-score method to identify unusual patterns
    """

    def __init__(self, baseline_window_days: int = 30):
        """
        Initialize anomaly detector

        Args:
            baseline_window_days: Number of days to use for baseline calculation
        """
        self.baseline_window_days = baseline_window_days

    def calculate_z_score(
        self,
        value: float,
        baseline_mean: float,
        baseline_std: float
    ) -> float:
        """
        Calculate z-score (standard deviations from mean)

        Args:
            value: Observed value
            baseline_mean: Mean of baseline
            baseline_std: Standard deviation of baseline

        Returns:
            Z-score (positive = above normal, negative = below normal)
        """
        if baseline_std == 0:
            return 0.0

        z_score = (value - baseline_mean) / baseline_std
        return round(z_score, 2)

    def classify_anomaly(self, z_score: float) -> Literal[
        "critical_anomaly", "significant_anomaly", "minor_anomaly", "normal"
    ]:
        """
        Classify anomaly severity based on z-score

        Args:
            z_score: Z-score value

        Returns:
            Anomaly classification
        """
        abs_z = abs(z_score)

        if abs_z > 3:
            return "critical_anomaly"
        elif abs_z > 2:
            return "significant_anomaly"
        elif abs_z > 1.5:
            return "minor_anomaly"
        else:
            return "normal"

    def detect_daily_anomalies(
        self,
        daily_features: Dict,
        baselines: Dict
    ) -> Dict:
        """
        Detect anomalies in daily features

        Args:
            daily_features: Features for a single day (from DailyAggregator)
            baselines: Historical baselines

        Returns:
            Anomaly flags and scores
        """
        anomalies = {
            'has_anomaly': False,
            'anomaly_types': [],
            'total_revenue_z': None,
            'category_anomalies': [],
            'location_anomalies': [],
        }

        # Check total revenue anomaly
        if 'total_revenue' in baselines and daily_features.get('daily_totals'):
            baseline = baselines['total_revenue']
            observed = daily_features['daily_totals']['total_revenue']

            z_score = self.calculate_z_score(
                observed,
                baseline['mean'],
                baseline['std']
            )

            anomalies['total_revenue_z'] = z_score
            classification = self.classify_anomaly(z_score)

            if classification != "normal":
                anomalies['has_anomaly'] = True
                anomalies['anomaly_types'].append('total_revenue')

        # Check category anomalies
        if daily_features.get('by_category') and baselines.get('by_category'):
            for category, metrics in daily_features['by_category'].items():
                if category not in baselines['by_category']:
                    continue

                baseline = baselines['by_category'][category]
                observed_revenue = metrics['revenue']

                z_score = self.calculate_z_score(
                    observed_revenue,
                    baseline['mean'],
                    baseline['std']
                )

                classification = self.classify_anomaly(z_score)

                if classification != "normal":
                    anomalies['category_anomalies'].append({
                        'category': category,
                        'z_score': z_score,
                        'classification': classification,
                        'observed': observed_revenue,
                        'baseline_mean': baseline['mean'],
                        'direction': 'above' if z_score > 0 else 'below',
                    })

                    anomalies['has_anomaly'] = True

        # Check location anomalies
        if daily_features.get('by_location') and baselines.get('by_location'):
            for location, metrics in daily_features['by_location'].items():
                if location not in baselines['by_location']:
                    continue

                baseline = baselines['by_location'][location]
                observed_revenue = metrics['revenue']

                z_score = self.calculate_z_score(
                    observed_revenue,
                    baseline['mean'],
                    baseline['std']
                )

                classification = self.classify_anomaly(z_score)

                if classification != "normal":
                    anomalies['location_anomalies'].append({
                        'location': location,
                        'z_score': z_score,
                        'classification': classification,
                        'observed': observed_revenue,
                        'baseline_mean': baseline['mean'],
                        'direction': 'above' if z_score > 0 else 'below',
                    })

                    anomalies['has_anomaly'] = True

        # Multi-dimensional anomaly check (reduces false positives)
        anomalies['is_true_anomaly'] = self._check_multidimensional_anomaly(anomalies)

        return anomalies

    def _check_multidimensional_anomaly(self, anomalies: Dict) -> bool:
        """
        Check if anomaly is significant across multiple dimensions

        Reduces false positives by requiring anomalies in multiple areas

        Args:
            anomalies: Anomaly dictionary

        Returns:
            True if it's a true multidimensional anomaly
        """
        # Count significant anomalies
        significant_category_anomalies = [
            a for a in anomalies['category_anomalies']
            if a['classification'] in ['critical_anomaly', 'significant_anomaly']
        ]

        significant_location_anomalies = [
            a for a in anomalies['location_anomalies']
            if a['classification'] in ['critical_anomaly', 'significant_anomaly']
        ]

        total_revenue_significant = (
            anomalies.get('total_revenue_z') and
            abs(anomalies['total_revenue_z']) > 2
        )

        # True anomaly if:
        # - 2+ categories are anomalous, OR
        # - 2+ locations are anomalous, OR
        # - Total revenue is significant AND at least 1 category/location
        if len(significant_category_anomalies) >= 2:
            return True

        if len(significant_location_anomalies) >= 2:
            return True

        if total_revenue_significant and (
            len(significant_category_anomalies) >= 1 or
            len(significant_location_anomalies) >= 1
        ):
            return True

        return False

    def calculate_baselines(
        self,
        sales_df: pd.DataFrame,
        end_date: date,
        window_days: int = 30
    ) -> Dict:
        """
        Calculate baseline statistics for anomaly detection

        Args:
            sales_df: Sales data
            end_date: End of baseline period
            window_days: Number of days for baseline

        Returns:
            Baseline statistics (mean, std) for different dimensions
        """
        sales_df = sales_df.copy()
        # Handle different date formats (dayfirst=True for DD/MM/YYYY format)
        sales_df['Sale Date'] = pd.to_datetime(sales_df['Sale Date'], dayfirst=True, format='mixed')
        sales_df['date'] = sales_df['Sale Date'].dt.date

        start_date = end_date - timedelta(days=window_days)

        baseline_data = sales_df[
            (sales_df['date'] >= start_date) &
            (sales_df['date'] <= end_date)
        ]

        baselines = {
            'calculation_date': str(end_date),
            'window_days': window_days,
            'start_date': str(start_date),
        }

        # Total revenue baseline
        daily_revenue = baseline_data.groupby('date')['Turnover'].sum()

        baselines['total_revenue'] = {
            'mean': float(daily_revenue.mean()),
            'std': float(daily_revenue.std()),
            'median': float(daily_revenue.median()),
            'min': float(daily_revenue.min()),
            'max': float(daily_revenue.max()),
        }

        # By category baselines
        baselines['by_category'] = {}

        categories = baseline_data['Dept Fullname'].unique()

        for category in categories:
            cat_data = baseline_data[baseline_data['Dept Fullname'] == category]
            daily_cat_revenue = cat_data.groupby('date')['Turnover'].sum()

            baselines['by_category'][category] = {
                'mean': float(daily_cat_revenue.mean()),
                'std': float(daily_cat_revenue.std()),
                'median': float(daily_cat_revenue.median()),
                'p95': float(daily_cat_revenue.quantile(0.95)),
            }

        # By location baselines
        baselines['by_location'] = {}

        locations = baseline_data['Branch Name'].unique()

        for location in locations:
            loc_data = baseline_data[baseline_data['Branch Name'] == location]
            daily_loc_revenue = loc_data.groupby('date')['Turnover'].sum()

            baselines['by_location'][location] = {
                'mean': float(daily_loc_revenue.mean()),
                'std': float(daily_loc_revenue.std()),
                'median': float(daily_loc_revenue.median()),
            }

        return baselines

    def detect_category_surge(
        self,
        category: str,
        observed_value: float,
        baseline: Dict,
        threshold_multiplier: float = 2.0
    ) -> Dict:
        """
        Detect if a category has surged (e.g., 2x normal)

        Args:
            category: Category name
            observed_value: Observed revenue/units
            baseline: Baseline statistics
            threshold_multiplier: Multiplier to trigger surge (e.g., 2.0 = 2x)

        Returns:
            Surge detection result
        """
        baseline_mean = baseline.get('mean', 0)

        if baseline_mean == 0:
            return {'is_surge': False}

        multiplier = observed_value / baseline_mean

        is_surge = multiplier >= threshold_multiplier

        return {
            'is_surge': is_surge,
            'category': category,
            'observed': observed_value,
            'baseline_mean': baseline_mean,
            'multiplier': round(multiplier, 2),
            'threshold': threshold_multiplier,
        }

    def detect_category_drought(
        self,
        category: str,
        observed_value: float,
        baseline: Dict,
        threshold_multiplier: float = 0.5
    ) -> Dict:
        """
        Detect if a category has dropped significantly (e.g., <0.5x normal)

        Args:
            category: Category name
            observed_value: Observed revenue/units
            baseline: Baseline statistics
            threshold_multiplier: Multiplier to trigger drought (e.g., 0.5 = 50% of normal)

        Returns:
            Drought detection result
        """
        baseline_mean = baseline.get('mean', 0)

        if baseline_mean == 0:
            return {'is_drought': False}

        multiplier = observed_value / baseline_mean

        is_drought = multiplier <= threshold_multiplier

        return {
            'is_drought': is_drought,
            'category': category,
            'observed': observed_value,
            'baseline_mean': baseline_mean,
            'multiplier': round(multiplier, 2),
            'threshold': threshold_multiplier,
        }

    def detect_high_volume_day(
        self,
        observed_revenue: float,
        baseline: Dict,
        percentile_threshold: float = 0.90
    ) -> bool:
        """
        Check if this is a high volume day (>90th percentile)

        Args:
            observed_revenue: Day's revenue
            baseline: Baseline statistics (must include p90 or p95)
            percentile_threshold: Threshold (0.90 = 90th percentile)

        Returns:
            True if high volume day
        """
        # Use p95 if available, otherwise calculate from mean/std
        if 'p95' in baseline:
            threshold = baseline['p95']
        else:
            # Approximate 90th percentile as mean + 1.28*std
            threshold = baseline['mean'] + (1.28 * baseline['std'])

        return observed_revenue > threshold

    def detect_low_volume_day(
        self,
        observed_revenue: float,
        baseline: Dict,
        percentile_threshold: float = 0.10
    ) -> bool:
        """
        Check if this is a low volume day (<10th percentile)

        Args:
            observed_revenue: Day's revenue
            baseline: Baseline statistics
            percentile_threshold: Threshold (0.10 = 10th percentile)

        Returns:
            True if low volume day
        """
        # Approximate 10th percentile as mean - 1.28*std
        threshold = baseline['mean'] - (1.28 * baseline['std'])

        return observed_revenue < threshold

    def generate_anomaly_report(self, anomalies: Dict) -> str:
        """
        Generate human-readable anomaly report

        Args:
            anomalies: Anomaly detection results

        Returns:
            Formatted report string
        """
        if not anomalies['has_anomaly']:
            return "No significant anomalies detected."

        report_lines = ["ANOMALY DETECTION REPORT", "=" * 60]

        # Overall revenue
        if anomalies.get('total_revenue_z'):
            z = anomalies['total_revenue_z']
            direction = "above" if z > 0 else "below"
            report_lines.append(
                f"Overall Revenue: {abs(z):.1f} std deviations {direction} normal"
            )

        # Category anomalies
        if anomalies['category_anomalies']:
            report_lines.append("\nCATEGORY ANOMALIES:")
            report_lines.append("-" * 60)

            for cat in sorted(
                anomalies['category_anomalies'],
                key=lambda x: abs(x['z_score']),
                reverse=True
            ):
                report_lines.append(
                    f"  {cat['category']:40s} | z={cat['z_score']:>6.2f} | "
                    f"{cat['classification']:20s} | "
                    f"€{cat['observed']:>8,.0f} vs €{cat['baseline_mean']:>8,.0f}"
                )

        # Location anomalies
        if anomalies['location_anomalies']:
            report_lines.append("\nLOCATION ANOMALIES:")
            report_lines.append("-" * 60)

            for loc in sorted(
                anomalies['location_anomalies'],
                key=lambda x: abs(x['z_score']),
                reverse=True
            ):
                report_lines.append(
                    f"  {loc['location']:40s} | z={loc['z_score']:>6.2f} | "
                    f"{loc['classification']:20s} | "
                    f"€{loc['observed']:>8,.0f} vs €{loc['baseline_mean']:>8,.0f}"
                )

        # True anomaly flag
        if anomalies['is_true_anomaly']:
            report_lines.append("\n⚠️  TRUE MULTIDIMENSIONAL ANOMALY DETECTED")
        else:
            report_lines.append("\nℹ️  Isolated anomaly (not multidimensional)")

        return "\n".join(report_lines)
