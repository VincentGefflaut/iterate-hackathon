"""
Time-Restricted Internet Search Examples
Multiple approaches to search for content before a specific date
"""

# ============================================================================
# METHOD 1: Google Custom Search API (Official, Best Quality)
# ============================================================================
"""
Google Custom Search JSON API allows date restrictions.
Requires API key from Google Cloud Console.

Pros:
- Official Google API
- Most reliable and accurate
- Structured JSON results
- Fine-grained date control

Cons:
- Requires API key (free tier: 100 queries/day)
- Need to set up Custom Search Engine

Setup:
1. Create project at https://console.cloud.google.com/
2. Enable Custom Search API
3. Create Custom Search Engine at https://cse.google.com/
4. Get API key and Search Engine ID
"""

def google_custom_search_with_date(query, api_key, cx, before_date=None):
    """
    Search Google with date restriction using official API

    Args:
        query: Search query string
        api_key: Google API key
        cx: Custom Search Engine ID
        before_date: Date string in format 'YYYY-MM-DD' or 'YYYYMMDD'
    """
    import requests

    url = "https://www.googleapis.com/customsearch/v1"

    params = {
        'key': api_key,
        'cx': cx,
        'q': query,
        'num': 10  # Results per page (max 10)
    }

    # Add date restriction
    if before_date:
        # Format: dateRestrict parameter
        # Can use: d[number] (days), w[number] (weeks), m[number] (months), y[number] (years)
        # OR use sort parameter with date range

        # Example: Results from before specific date
        # Use 'sort' parameter with date range
        params['sort'] = f'date:r:19700101:{before_date.replace("-", "")}'
        # Format: date:r:YYYYMMDD:YYYYMMDD (start:end)

    response = requests.get(url, params=params)

    if response.status_code == 200:
        results = response.json()
        return results.get('items', [])
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return []

# Example usage:
# results = google_custom_search_with_date(
#     query="retail operations AI",
#     api_key="YOUR_API_KEY",
#     cx="YOUR_SEARCH_ENGINE_ID",
#     before_date="2024-01-01"
# )


# ============================================================================
# METHOD 2: DuckDuckGo (No API Key, Simple)
# ============================================================================
"""
DuckDuckGo doesn't have official date filtering in API,
but you can use the duckduckgo_search library for basic searches
then filter results by checking page metadata.

Pros:
- No API key needed
- Privacy-focused
- Simple to use

Cons:
- No built-in date filtering
- Less precise than Google
- Need to parse results manually
"""

def duckduckgo_search_simple(query, max_results=10):
    """
    Simple DuckDuckGo search (no date filtering built-in)
    """
    from duckduckgo_search import DDGS

    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=max_results):
            results.append({
                'title': r.get('title'),
                'url': r.get('href'),
                'snippet': r.get('body')
            })

    return results

# Note: To filter by date, you'd need to fetch each page and check metadata
# or use archive.org for historical snapshots


# ============================================================================
# METHOD 3: SerpAPI (Paid, Easy to Use)
# ============================================================================
"""
SerpAPI provides Google search results with date filtering.

Pros:
- Very easy to use
- Handles Google, Bing, Yahoo, etc.
- Built-in date filtering
- Well-documented

Cons:
- Paid service (free tier: 100 searches/month)
"""

def serpapi_search_with_date(query, api_key, before_date=None):
    """
    Search using SerpAPI with date restriction

    Args:
        query: Search query
        api_key: SerpAPI key
        before_date: Date string 'YYYY-MM-DD'
    """
    import requests

    params = {
        'q': query,
        'api_key': api_key,
        'engine': 'google',
        'num': 10
    }

    # Add date restriction
    if before_date:
        # SerpAPI uses 'tbs' parameter (same as Google)
        # cd_min and cd_max for date range
        params['tbs'] = f'cdr:1,cd_max:{before_date.replace("-", "/")}'

    response = requests.get('https://serpapi.com/search', params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get('organic_results', [])
    else:
        return []


# ============================================================================
# METHOD 4: Direct Google URL with TBS Parameter (Scraping)
# ============================================================================
"""
Google uses the 'tbs' parameter for date filtering.
You can construct URLs and scrape results.

WARNING: Google may block scraping. Use responsibly and consider rate limiting.

Pros:
- No API key needed
- Direct Google results
- Free

Cons:
- Against Google ToS (may get blocked)
- Need to parse HTML
- Fragile (breaks if Google changes HTML)
- May require handling CAPTCHAs
"""

def google_search_url_with_date(query, before_date):
    """
    Construct Google search URL with date restriction

    Args:
        query: Search query
        before_date: Date in format 'YYYY-MM-DD'

    Returns:
        URL string (you'd need to fetch and parse)
    """
    import urllib.parse

    # Convert date to Google's format
    # cd_max format: MM/DD/YYYY
    from datetime import datetime
    date_obj = datetime.strptime(before_date, '%Y-%m-%d')
    cd_max = date_obj.strftime('%m/%d/%Y')

    # Construct tbs parameter
    # cdr:1 = custom date range
    # cd_min = start date
    # cd_max = end date
    tbs = f'cdr:1,cd_max:{cd_max}'

    # Build URL
    base_url = 'https://www.google.com/search'
    params = {
        'q': query,
        'tbs': tbs
    }

    url = f"{base_url}?{urllib.parse.urlencode(params)}"
    return url

# Example:
# url = google_search_url_with_date("AI retail operations", "2023-12-31")
# print(url)
# https://www.google.com/search?q=AI+retail+operations&tbs=cdr%3A1%2Ccd_max%3A12%2F31%2F2023

# To actually fetch and parse (with BeautifulSoup):
"""
import requests
from bs4 import BeautifulSoup

def scrape_google_with_date(query, before_date):
    url = google_search_url_with_date(query, before_date)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Parse results (structure changes frequently!)
    results = []
    for g in soup.find_all('div', class_='g'):
        title = g.find('h3')
        link = g.find('a')
        snippet = g.find('div', class_='VwiC3b')

        if title and link:
            results.append({
                'title': title.get_text(),
                'url': link.get('href'),
                'snippet': snippet.get_text() if snippet else ''
            })

    return results
"""


# ============================================================================
# METHOD 5: Bing Search API (Microsoft)
# ============================================================================
"""
Bing Search API has good date filtering support.

Pros:
- Official Microsoft API
- Good date filtering
- Generous free tier (1000 queries/month)

Cons:
- Requires Azure account
- Different result quality than Google
"""

def bing_search_with_date(query, api_key, before_date=None):
    """
    Search using Bing with date restriction

    Args:
        query: Search query
        api_key: Bing Search API key
        before_date: Date string 'YYYY-MM-DD'
    """
    import requests

    endpoint = "https://api.bing.microsoft.com/v7.0/search"

    headers = {'Ocp-Apim-Subscription-Key': api_key}
    params = {
        'q': query,
        'count': 10
    }

    # Add date filter
    if before_date:
        # Bing uses 'freshness' parameter
        # But for specific dates, use query modifier
        params['q'] = f'{query} before:{before_date}'

    response = requests.get(endpoint, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()
        return data.get('webPages', {}).get('value', [])
    else:
        return []


# ============================================================================
# METHOD 6: Internet Archive (Wayback Machine)
# ============================================================================
"""
For truly historical searches, use Internet Archive's Wayback Machine.

Pros:
- Access archived versions of websites
- Can search specific dates in the past
- Free API

Cons:
- Not all pages are archived
- Not a search engine (need to know URLs)
- Limited to archived content
"""

def wayback_get_snapshot(url, before_date):
    """
    Get archived snapshot of a URL before a specific date

    Args:
        url: Website URL
        before_date: Date string 'YYYYMMDD'
    """
    import requests

    # Wayback Machine API
    api_url = f"http://archive.org/wayback/available"

    params = {
        'url': url,
        'timestamp': before_date
    }

    response = requests.get(api_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data.get('archived_snapshots', {}).get('closest'):
            snapshot = data['archived_snapshots']['closest']
            return snapshot['url']  # URL to archived version

    return None

# Example:
# snapshot_url = wayback_get_snapshot('https://example.com', '20230101')


# ============================================================================
# PRACTICAL EXAMPLE: Search for Retail AI Articles Before 2024
# ============================================================================

def search_retail_ai_before_2024():
    """
    Practical example: Find retail AI articles published before 2024
    """

    # Using Google Custom Search (if you have API key)
    # results = google_custom_search_with_date(
    #     query="AI retail operations automation",
    #     api_key="YOUR_KEY",
    #     cx="YOUR_CX",
    #     before_date="2024-01-01"
    # )

    # Using URL construction (for manual checking)
    url = google_search_url_with_date(
        query="AI retail operations automation",
        before_date="2024-01-01"
    )

    print("Google Search URL with date filter:")
    print(url)
    print("\nThis URL will show results from before January 1, 2024")
    print("\nTBS parameter breakdown:")
    print("  cdr:1 = custom date range")
    print("  cd_max:01/01/2024 = before this date")

    # Alternative: Search for specific time period
    url2 = google_search_url_with_date_range(
        query="AI retail operations",
        start_date="2020-01-01",
        end_date="2023-12-31"
    )
    print(f"\n\nSpecific date range URL:")
    print(url2)

def google_search_url_with_date_range(query, start_date, end_date):
    """
    Google search between two dates
    """
    import urllib.parse
    from datetime import datetime

    start = datetime.strptime(start_date, '%Y-%m-%d').strftime('%m/%d/%Y')
    end = datetime.strptime(end_date, '%Y-%m-%d').strftime('%m/%d/%Y')

    tbs = f'cdr:1,cd_min:{start},cd_max:{end}'

    base_url = 'https://www.google.com/search'
    params = {
        'q': query,
        'tbs': tbs
    }

    return f"{base_url}?{urllib.parse.urlencode(params)}"


# ============================================================================
# BEST PRACTICES & TIPS
# ============================================================================
"""
1. For Production Use:
   - Use official APIs (Google Custom Search, Bing)
   - Implement rate limiting
   - Cache results to avoid repeated queries
   - Handle errors gracefully

2. For Research/Personal Use:
   - URL construction is fine for one-off searches
   - DuckDuckGo is good for privacy
   - Consider using multiple sources

3. Date Filtering Tips:
   - Google's date filter isn't perfect (relies on page metadata)
   - Some pages may appear even if published after your date
   - Combine with keyword filtering (e.g., "before:2024-01-01" in query)

4. Alternative Approaches:
   - Use news APIs (NewsAPI, GDELT) for time-filtered news
   - Academic search engines (Google Scholar, Semantic Scholar) have date filters
   - Twitter API has precise timestamp filtering
"""


# ============================================================================
# HACKATHON USE CASE
# ============================================================================

def search_source_retail_info():
    """
    Example: Search for information about Source.shop (from hackathon)
    focusing on content before the hackathon announcement
    """

    queries = [
        "source.shop AI procurement",
        "source.shop retail operations",
        "AI native ERP retail",
        "retail operations automation AI"
    ]

    before_date = "2024-11-01"  # Before November 2024

    for query in queries:
        url = google_search_url_with_date(query, before_date)
        print(f"\nQuery: {query}")
        print(f"URL: {url}\n")
        print("-" * 80)


if __name__ == "__main__":
    print("TIME-RESTRICTED INTERNET SEARCH EXAMPLES")
    print("=" * 80)

    print("\n1. Generating search URLs with date restrictions...")
    search_retail_ai_before_2024()

    print("\n\n2. Searching for Source.shop information (pre-hackathon)...")
    search_source_retail_info()

    print("\n" + "=" * 80)
    print("RECOMMENDED APPROACH FOR YOUR USE CASE:")
    print("=" * 80)
    print("""
    For the hackathon, you likely want to:

    1. Research competitors/existing solutions BEFORE the hackathon was announced
    2. Find relevant research papers/articles on retail AI
    3. Discover what tools already exist

    Best options:

    A. Quick Research (Manual):
       - Use the generated Google URLs with tbs parameter
       - Open in browser, browse results
       - No coding needed, instant results

    B. Automated Research (Script):
       - Use Google Custom Search API (free tier: 100/day)
       - Store results in CSV for analysis
       - Build knowledge base

    C. Academic Research:
       - Google Scholar has built-in date filters
       - Semantic Scholar API for papers
       - arXiv for recent AI research

    Want me to set up any of these for your specific needs?
    """)
