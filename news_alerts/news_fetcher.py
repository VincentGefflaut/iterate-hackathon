"""
News fetcher from multiple sources for Irish/Dublin news.

Supports:
- NewsAPI.org (requires API key)
- Google News RSS feeds
- Met Éireann weather alerts (Irish meteorological service)
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Optional
import os
from pathlib import Path

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    # Look for .env in project root (two levels up from this file)
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    # python-dotenv not installed, will fall back to system env vars
    pass

from .models import NewsArticle


class NewsFetcher:
    """Fetches news from multiple sources"""

    def __init__(self, newsapi_key: Optional[str] = None):
        """
        Initialize news fetcher

        Args:
            newsapi_key: Optional NewsAPI.org API key (can also set NEWS_API_KEY env var)
        """
        self.newsapi_key = newsapi_key or os.getenv("NEWS_API_KEY")

    def fetch_all(self, query: str = "Ireland OR Dublin", days_back: int = 1) -> List[NewsArticle]:
        """
        Fetch news from all sources

        Args:
            query: Search query
            days_back: How many days of news to fetch

        Returns:
            List of NewsArticle objects
        """
        articles = []

        # Fetch from each source
        try:
            articles.extend(self.fetch_newsapi(query, days_back))
        except Exception as e:
            print(f"Warning: NewsAPI fetch failed: {e}")

        try:
            articles.extend(self.fetch_google_news(query))
        except Exception as e:
            print(f"Warning: Google News fetch failed: {e}")

        try:
            articles.extend(self.fetch_met_eireann())
        except Exception as e:
            print(f"Warning: Met Éireann fetch failed: {e}")

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def fetch_newsapi(self, query: str, days_back: int = 1) -> List[NewsArticle]:
        """
        Fetch from NewsAPI.org

        Requires API key (100 free requests/day)
        Get key at: https://newsapi.org/
        """
        if not self.newsapi_key:
            print("No NewsAPI key provided. Skipping NewsAPI.")
            return []

        from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")

        url = "https://newsapi.org/v2/everything"
        params = {
            "apiKey": self.newsapi_key,
            "q": query,
            "language": "en",
            "from": from_date,
            "sortBy": "publishedAt",
            "pageSize": 50  # Max 50 per request
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        articles = []
        for item in data.get("articles", []):
            articles.append(NewsArticle(
                title=item.get("title", ""),
                description=item.get("description", ""),
                content=item.get("content", ""),
                url=item.get("url", ""),
                published_at=item.get("publishedAt", datetime.now().isoformat()),
                source=f"NewsAPI: {item.get('source', {}).get('name', 'Unknown')}",
                author=item.get("author")
            ))

        return articles

    def fetch_google_news(self, query: str = "Ireland health OR Dublin events") -> List[NewsArticle]:
        """
        Fetch from Google News RSS feeds

        Free, no API key required
        """
        # Google News RSS feed URL
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=en-IE&gl=IE&ceid=IE:en"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            articles = []
            # Find all item elements (RSS items)
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_date_elem = item.find('pubDate')

                articles.append(NewsArticle(
                    title=title_elem.text if title_elem is not None else "",
                    description=desc_elem.text if desc_elem is not None else "",
                    content=desc_elem.text if desc_elem is not None else "",
                    url=link_elem.text if link_elem is not None else "",
                    published_at=pub_date_elem.text if pub_date_elem is not None else datetime.now().isoformat(),
                    source="Google News",
                    author=None
                ))

            return articles
        except Exception as e:
            print(f"Error fetching Google News: {e}")
            return []

    def fetch_met_eireann(self) -> List[NewsArticle]:
        """
        Fetch weather warnings from Met Éireann (Irish weather service)

        Free, no API key required
        Uses RSS feed
        """
        url = "https://www.met.ie/rss/warnings.xml"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            articles = []
            # Find all item elements
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                desc_elem = item.find('description')
                pub_date_elem = item.find('pubDate')

                articles.append(NewsArticle(
                    title=title_elem.text if title_elem is not None else "",
                    description=desc_elem.text if desc_elem is not None else "",
                    content=desc_elem.text if desc_elem is not None else "",
                    url=link_elem.text if link_elem is not None else "",
                    published_at=pub_date_elem.text if pub_date_elem is not None else datetime.now().isoformat(),
                    source="Met Éireann",
                    author="Met Éireann"
                ))

            return articles
        except Exception as e:
            print(f"Error fetching Met Éireann: {e}")
            return []

    def fetch_irish_health_news(self) -> List[NewsArticle]:
        """
        Fetch health-related news specifically for Ireland

        Combines multiple sources with health-focused queries
        """
        health_queries = [
            "Ireland health outbreak",
            "Dublin hospital",
            "Ireland disease",
            "Ireland virus flu",
            "Ireland health alert"
        ]

        all_articles = []
        for query in health_queries:
            try:
                articles = self.fetch_google_news(query)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Error fetching health news for '{query}': {e}")

        # Deduplicate
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles

    def fetch_dublin_events_news(self) -> List[NewsArticle]:
        """
        Fetch event-related news for Dublin

        Concerts, festivals, conferences, sporting events
        """
        event_queries = [
            "Dublin concert",
            "Dublin festival",
            "Dublin conference",
            "Dublin sporting event",
            "3Arena event",
            "Croke Park event",
            "Aviva Stadium event"
        ]

        all_articles = []
        for query in event_queries:
            try:
                articles = self.fetch_google_news(query)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Error fetching event news for '{query}': {e}")

        # Deduplicate
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article.url not in seen_urls:
                seen_urls.add(article.url)
                unique_articles.append(article)

        return unique_articles


# Example usage
if __name__ == "__main__":
    fetcher = NewsFetcher()

    print("Fetching Irish health news...")
    health_articles = fetcher.fetch_irish_health_news()
    print(f"Found {len(health_articles)} health articles")

    print("\nFetching Dublin events news...")
    event_articles = fetcher.fetch_dublin_events_news()
    print(f"Found {len(event_articles)} event articles")

    print("\nFetching weather alerts...")
    weather_articles = fetcher.fetch_met_eireann()
    print(f"Found {len(weather_articles)} weather alerts")

    # Print sample
    if health_articles:
        print(f"\nSample health article:")
        print(f"  Title: {health_articles[0].title}")
        print(f"  Source: {health_articles[0].source}")
        print(f"  URL: {health_articles[0].url}")
