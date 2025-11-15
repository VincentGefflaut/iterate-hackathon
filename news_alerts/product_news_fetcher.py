"""
Product-aware news fetcher that queries based on locations and top products.

Integrates with top.csv data to fetch targeted news.
"""

import requests
from typing import List, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path

try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

from .news_fetcher import NewsFetcher
from .models import NewsArticle
from .top_products_loader import TopProductsLoader, LocationProducts


class ProductNewsFetcher(NewsFetcher):
    """
    Extended news fetcher that queries based on location and product combinations.

    Combines top products data with news fetching to get relevant articles.
    """

    def __init__(self, newsapi_key: Optional[str] = None, csv_path: Optional[str] = None):
        """
        Initialize product-aware news fetcher

        Args:
            newsapi_key: Optional NewsAPI key
            csv_path: Optional path to top.csv file
        """
        super().__init__(newsapi_key)
        self.products_loader = TopProductsLoader(csv_path)

    def fetch_product_news(
        self,
        locations: List[LocationProducts] = None,
        max_articles_per_query: int = 10,
        days_back: int = 1
    ) -> List[NewsArticle]:
        """
        Fetch news articles based on locations and their top products

        Args:
            locations: List of LocationProducts to query (default: top 5 locations)
            max_articles_per_query: Max articles per location+product query
            days_back: How many days of news to fetch

        Returns:
            List of NewsArticle objects
        """
        if locations is None:
            # Use top 5 locations by default to control API costs
            locations = self.products_loader.get_top_locations(5)

        all_articles = []
        queries_made = 0

        print(f"\nFetching product news for {len(locations)} locations...")

        for location in locations:
            print(f"\n  Location: {location.location_name}")
            print(f"    Top products: {', '.join(location.top_products)}")

            # Create queries combining location + each top product
            for product in location.top_products:
                query = self._build_product_query(location, product)
                print(f"    Querying: {query}")

                try:
                    # Fetch from NewsAPI if available
                    articles = self._fetch_product_newsapi(query, days_back, max_articles_per_query)

                    if articles:
                        print(f"      Found {len(articles)} articles")
                        all_articles.extend(articles)
                        queries_made += 1
                    else:
                        # Fallback to Google News
                        articles = self.fetch_google_news(query)
                        if articles:
                            # Limit results
                            articles = articles[:max_articles_per_query]
                            print(f"      Found {len(articles)} articles (Google News)")
                            all_articles.extend(articles)

                except Exception as e:
                    print(f"      Error: {e}")
                    continue

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        print(f"\nTotal unique articles fetched: {len(unique_articles)}")
        print(f"Queries made: {queries_made}")

        return unique_articles

    def fetch_location_news(
        self,
        location: LocationProducts,
        include_products: bool = True,
        days_back: int = 1
    ) -> List[NewsArticle]:
        """
        Fetch news for a specific location and its products

        Args:
            location: LocationProducts object
            include_products: Whether to include product-specific queries
            days_back: How many days of news to fetch

        Returns:
            List of NewsArticle objects
        """
        articles = []

        # General location news (health, events, etc.)
        location_query = f"{location.province} Ireland news"
        print(f"Fetching general news for {location.location_name}...")

        try:
            general_articles = self.fetch_newsapi(location_query, days_back)
            articles.extend(general_articles)
        except Exception as e:
            print(f"  Error fetching general news: {e}")

        # Product-specific news if requested
        if include_products:
            for product in location.top_products:
                query = self._build_product_query(location, product)
                print(f"  Fetching product news: {query}")

                try:
                    product_articles = self.fetch_newsapi(query, days_back)
                    articles.extend(product_articles)
                except Exception as e:
                    print(f"    Error: {e}")

        # Deduplicate
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def fetch_health_and_product_news(
        self,
        top_n_locations: int = 5,
        days_back: int = 1
    ) -> List[NewsArticle]:
        """
        Fetch health news and product-related news for top locations

        Combines general health alerts with product-specific news

        Args:
            top_n_locations: Number of top locations to query
            days_back: How many days of news to fetch

        Returns:
            List of NewsArticle objects
        """
        articles = []

        # Get top locations
        locations = self.products_loader.get_top_locations(top_n_locations)

        print(f"Fetching health & product news for top {top_n_locations} locations...")

        # 1. Fetch general health news for Ireland
        print("\n1. Fetching general Irish health news...")
        try:
            health_articles = self.fetch_irish_health_news()
            articles.extend(health_articles)
            print(f"   Found {len(health_articles)} health articles")
        except Exception as e:
            print(f"   Error: {e}")

        # 2. Fetch product-related news for each location
        print("\n2. Fetching product-specific news by location...")
        for location in locations:
            for product in location.top_products:
                # Create targeted queries
                queries = [
                    f"{product} Ireland shortage",
                    f"{product} Ireland recall",
                    f"{product} Ireland demand",
                    f"{location.province} {product}"
                ]

                for query in queries[:2]:  # Limit to 2 queries per product to control API costs
                    try:
                        product_articles = self.fetch_newsapi(query, days_back)
                        if product_articles:
                            articles.extend(product_articles[:5])  # Max 5 articles per query
                            print(f"   {location.province} - {product}: {len(product_articles)} articles")
                    except Exception as e:
                        continue

        # Deduplicate
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        print(f"\nTotal unique articles: {len(unique_articles)}")
        return unique_articles

    def _build_product_query(self, location: LocationProducts, product: str) -> str:
        """
        Build a news query combining location and product

        Args:
            location: LocationProducts object
            product: Product name

        Returns:
            Query string
        """
        # Use province name (more specific than country)
        location_name = location.province

        # Build query variants based on product type
        if "Vitamins" in product or "Supplements" in product:
            query = f"{location_name} Ireland (vitamins OR supplements OR health OR shortage OR demand)"
        elif "Cleanser" in product or "Serum" in product:
            query = f"{location_name} Ireland (skincare OR beauty OR cosmetics OR shortage OR demand)"
        else:
            query = f"{location_name} Ireland {product} (shortage OR demand OR recall OR trend)"

        return query

    def _fetch_product_newsapi(
        self,
        query: str,
        days_back: int = 1,
        max_results: int = 10
    ) -> List[NewsArticle]:
        """
        Fetch from NewsAPI with result limiting

        Args:
            query: Search query
            days_back: How many days of news
            max_results: Maximum results to return

        Returns:
            List of NewsArticle objects (limited to max_results)
        """
        articles = self.fetch_newsapi(query, days_back)
        return articles[:max_results] if articles else []


# Example usage
if __name__ == "__main__":
    import os

    # Check if API key is set
    if not os.getenv("NEWS_API_KEY"):
        print("Warning: NEWS_API_KEY not set. Using demo mode.")
        print("Set NEWS_API_KEY in .env to fetch real news.")
        exit(0)

    fetcher = ProductNewsFetcher()

    # Test 1: Fetch for top 3 locations
    print("=" * 80)
    print("TEST 1: Fetch product news for top 3 locations")
    print("=" * 80)

    top_locations = fetcher.products_loader.get_top_locations(3)
    articles = fetcher.fetch_product_news(top_locations, max_articles_per_query=5)

    print(f"\nTotal articles: {len(articles)}")
    if articles:
        print("\nSample articles:")
        for i, article in enumerate(articles[:3], 1):
            print(f"\n{i}. {article.title}")
            print(f"   Source: {article.source}")
            print(f"   URL: {article.url}")

    # Test 2: Health + product news
    print("\n" + "=" * 80)
    print("TEST 2: Fetch health & product news")
    print("=" * 80)

    health_articles = fetcher.fetch_health_and_product_news(top_n_locations=3)
    print(f"\nTotal articles: {len(health_articles)}")
