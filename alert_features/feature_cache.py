"""
Feature Caching Layer
Stores and retrieves daily features efficiently
"""

import json
import pandas as pd
from datetime import datetime, date, timedelta
from pathlib import Path
from typing import Dict, List, Optional


class FeatureCache:
    """
    Manages caching of daily features to disk

    Stores features as JSON files for fast access
    """

    def __init__(self, cache_dir: str = "data/cache/daily_features"):
        """
        Initialize feature cache

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.baselines_file = self.cache_dir / "baselines.json"

    def save_daily_features(self, features: Dict, target_date: date) -> None:
        """
        Save daily features to cache

        Args:
            features: Daily features dictionary
            target_date: Date the features are for
        """
        filename = self._get_filename(target_date)

        with open(filename, 'w') as f:
            json.dump(features, f, indent=2, default=str)

        print(f"  💾 Saved features to {filename}")

    def load_daily_features(self, target_date: date) -> Optional[Dict]:
        """
        Load daily features from cache

        Args:
            target_date: Date to load features for

        Returns:
            Features dictionary or None if not cached
        """
        filename = self._get_filename(target_date)

        if not filename.exists():
            return None

        with open(filename, 'r') as f:
            features = json.load(f)

        return features

    def save_baselines(self, baselines: Dict) -> None:
        """
        Save baseline statistics

        Args:
            baselines: Baseline statistics dictionary
        """
        with open(self.baselines_file, 'w') as f:
            json.dump(baselines, f, indent=2, default=str)

        print(f"  💾 Saved baselines to {self.baselines_file}")

    def load_baselines(self) -> Optional[Dict]:
        """
        Load baseline statistics

        Returns:
            Baselines dictionary or None if not cached
        """
        if not self.baselines_file.exists():
            return None

        with open(self.baselines_file, 'r') as f:
            baselines = json.load(f)

        return baselines

    def _get_filename(self, target_date: date) -> Path:
        """Get filename for a specific date"""
        return self.cache_dir / f"{target_date.isoformat()}.json"

    def has_features(self, target_date: date) -> bool:
        """Check if features exist for a date"""
        return self._get_filename(target_date).exists()

    def list_cached_dates(self) -> List[date]:
        """
        List all dates with cached features

        Returns:
            List of dates (sorted)
        """
        dates = []

        for file in self.cache_dir.glob("*.json"):
            if file.stem == "baselines":
                continue

            try:
                date_obj = datetime.fromisoformat(file.stem).date()
                dates.append(date_obj)
            except ValueError:
                pass

        dates.sort()
        return dates

    def get_latest_cached_date(self) -> Optional[date]:
        """
        Get the most recent cached date

        Returns:
            Latest date or None
        """
        dates = self.list_cached_dates()

        if not dates:
            return None

        return dates[-1]

    def delete_old_cache(self, keep_days: int = 90) -> int:
        """
        Delete cache files older than N days

        Args:
            keep_days: Number of days to keep

        Returns:
            Number of files deleted
        """
        cutoff_date = date.today() - timedelta(days=keep_days)

        deleted = 0

        for file in self.cache_dir.glob("*.json"):
            if file.stem == "baselines":
                continue

            try:
                date_obj = datetime.fromisoformat(file.stem).date()

                if date_obj < cutoff_date:
                    file.unlink()
                    deleted += 1
            except ValueError:
                pass

        if deleted > 0:
            print(f"  🗑️  Deleted {deleted} old cache files")

        return deleted

    def get_date_range_features(
        self,
        start_date: date,
        end_date: date
    ) -> List[Dict]:
        """
        Load features for a date range

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of features (missing dates will be skipped)
        """
        features_list = []

        current_date = start_date

        while current_date <= end_date:
            features = self.load_daily_features(current_date)

            if features is not None:
                features_list.append(features)

            current_date += timedelta(days=1)

        return features_list

    def export_to_csv(
        self,
        output_file: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> None:
        """
        Export cached features to CSV for analysis

        Args:
            output_file: Path to output CSV
            start_date: Optional start date filter
            end_date: Optional end date filter
        """
        dates = self.list_cached_dates()

        if start_date:
            dates = [d for d in dates if d >= start_date]

        if end_date:
            dates = [d for d in dates if d <= end_date]

        # Collect daily totals
        rows = []

        for target_date in dates:
            features = self.load_daily_features(target_date)

            if features and features.get('daily_totals'):
                totals = features['daily_totals']

                row = {
                    'date': target_date,
                    **totals
                }

                # Add historical context
                if features.get('historical_context'):
                    ctx = features['historical_context']
                    row['7_day_avg'] = ctx.get('7_day_average')
                    row['30_day_avg'] = ctx.get('30_day_average')

                # Add anomaly flags
                if features.get('anomalies'):
                    anom = features['anomalies']
                    row['has_anomaly'] = anom.get('has_anomaly', False)
                    row['is_true_anomaly'] = anom.get('is_true_anomaly', False)

                rows.append(row)

        df = pd.DataFrame(rows)
        df.to_csv(output_file, index=False)

        print(f"  📊 Exported {len(rows)} days to {output_file}")

    def get_cache_stats(self) -> Dict:
        """
        Get statistics about the cache

        Returns:
            Cache statistics
        """
        dates = self.list_cached_dates()

        if not dates:
            return {
                'total_cached_days': 0,
                'oldest_date': None,
                'newest_date': None,
                'has_baselines': self.baselines_file.exists(),
            }

        # Calculate total cache size
        total_size = sum(
            f.stat().st_size
            for f in self.cache_dir.glob("*.json")
        )

        return {
            'total_cached_days': len(dates),
            'oldest_date': str(dates[0]),
            'newest_date': str(dates[-1]),
            'has_baselines': self.baselines_file.exists(),
            'cache_size_mb': round(total_size / (1024 * 1024), 2),
            'cache_directory': str(self.cache_dir.absolute()),
        }

    def print_cache_stats(self) -> None:
        """Print cache statistics in a nice format"""
        stats = self.get_cache_stats()

        print("\n" + "=" * 60)
        print("FEATURE CACHE STATISTICS")
        print("=" * 60)

        if stats['total_cached_days'] == 0:
            print("Cache is empty")
            return

        print(f"Total cached days:  {stats['total_cached_days']:,}")
        print(f"Oldest date:        {stats['oldest_date']}")
        print(f"Newest date:        {stats['newest_date']}")
        print(f"Has baselines:      {stats['has_baselines']}")
        print(f"Cache size:         {stats['cache_size_mb']:.2f} MB")
        print(f"Cache directory:    {stats['cache_directory']}")
        print("=" * 60)
