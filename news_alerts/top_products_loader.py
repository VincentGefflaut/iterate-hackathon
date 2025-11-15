"""
Load and parse top products by location from CSV.
"""

import csv
from pathlib import Path
from typing import List, Dict, Set
from dataclasses import dataclass


@dataclass
class LocationProducts:
    """Top products for a specific location"""
    country: str
    province: str
    total_sold: int
    top_products: List[str]

    @property
    def location_name(self) -> str:
        """Get full location name"""
        return f"{self.province}, {self.country}"


class TopProductsLoader:
    """Load top products by location from CSV"""

    def __init__(self, csv_path: str = None):
        """
        Initialize loader

        Args:
            csv_path: Path to top.csv file (default: top.csv in project root)
        """
        if csv_path is None:
            # Default to top.csv in project root
            csv_path = Path(__file__).parent.parent / "top.csv"

        self.csv_path = Path(csv_path)
        self._locations: List[LocationProducts] = []
        self._load()

    def _load(self):
        """Load and parse CSV file"""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.csv_path}")

        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Skip empty rows
                if not row.get('shipping_province'):
                    continue

                # Extract top products
                top_products = []
                for i in [1, 2, 3]:
                    product = row.get(f'top{i}_productType', '').strip()
                    if product:
                        top_products.append(product)

                # Create LocationProducts object
                location = LocationProducts(
                    country=row['shipping_country'].strip(),
                    province=row['shipping_province'].strip(),
                    total_sold=int(row['total_n_sold']) if row.get('total_n_sold') else 0,
                    top_products=top_products
                )

                self._locations.append(location)

    def get_all_locations(self) -> List[LocationProducts]:
        """Get all locations with their top products"""
        return self._locations

    def get_top_locations(self, n: int = 5) -> List[LocationProducts]:
        """
        Get top N locations by sales volume

        Args:
            n: Number of locations to return

        Returns:
            List of top N LocationProducts sorted by total_sold
        """
        sorted_locations = sorted(self._locations, key=lambda x: x.total_sold, reverse=True)
        return sorted_locations[:n]

    def get_unique_products(self) -> Set[str]:
        """Get set of all unique products across all locations"""
        products = set()
        for location in self._locations:
            products.update(location.top_products)
        return products

    def get_unique_provinces(self) -> Set[str]:
        """Get set of all unique provinces"""
        return {loc.province for loc in self._locations}

    def get_locations_by_country(self, country: str) -> List[LocationProducts]:
        """
        Get all locations for a specific country

        Args:
            country: Country name (e.g., "Ireland", "United Kingdom")

        Returns:
            List of LocationProducts for that country
        """
        return [loc for loc in self._locations if loc.country == country]


# Example usage
if __name__ == "__main__":
    loader = TopProductsLoader()

    print("Top 5 Locations by Sales:")
    print("-" * 60)
    for loc in loader.get_top_locations(5):
        print(f"{loc.location_name}")
        print(f"  Total sold: {loc.total_sold:,}")
        print(f"  Top products: {', '.join(loc.top_products)}")
        print()

    print("\nUnique Products:")
    print("-" * 60)
    for product in sorted(loader.get_unique_products()):
        print(f"  - {product}")

    print("\nAll Locations:")
    print("-" * 60)
    for loc in loader.get_all_locations():
        print(f"  - {loc.location_name}: {', '.join(loc.top_products)}")
