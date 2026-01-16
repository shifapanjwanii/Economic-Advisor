"""NewsAPI tool for financial news aggregation.

Provides access to real-time economic and financial news headlines
from hundreds of reputable sources.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import httpx

NEWS_API_BASE_URL = "https://newsapi.org/v2"


def _get_api_key() -> str:
    """Get NewsAPI key from environment."""
    return os.getenv("NEWS_API_KEY", "")


async def _fetch_news(
    query: str,
    category: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    page_size: int = 10,
    sort_by: str = "relevancy",
) -> dict:
    """Fetch news from NewsAPI.

    Args:
        query: Search query for news articles.
        category: News category filter.
        from_date: Start date (YYYY-MM-DD format).
        to_date: End date (YYYY-MM-DD format).
        page_size: Number of articles to return.
        sort_by: Sort order ('relevancy', 'popularity', 'publishedAt').

    Returns:
        Dict containing news articles or error message.
    """
    api_key = _get_api_key()

    if not api_key:
        return {
            "error": "NEWS_API_KEY not configured. Please set the environment variable.",
            "articles": _get_mock_news(query),
        }

    # Default date range: last 7 days
    if not to_date:
        to_date = datetime.now().strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    params = {
        "q": query,
        "apiKey": api_key,
        "from": from_date,
        "to": to_date,
        "pageSize": page_size,
        "sortBy": sort_by,
        "language": "en",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{NEWS_API_BASE_URL}/everything",
                params=params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        return {"error": f"Failed to fetch news: {str(e)}"}


def _get_mock_news(query: str) -> list:
    """Return mock news data when API key is not available."""
    return [
        {
            "title": f"[Demo] Economic outlook remains uncertain amid {query} concerns",
            "description": "This is demo data. Configure NEWS_API_KEY for real news.",
            "source": {"name": "Demo Source"},
            "publishedAt": datetime.now().isoformat(),
            "url": "https://newsapi.org",
        },
        {
            "title": f"[Demo] Markets react to latest {query} developments",
            "description": "This is demo data. Configure NEWS_API_KEY for real news.",
            "source": {"name": "Demo Source"},
            "publishedAt": datetime.now().isoformat(),
            "url": "https://newsapi.org",
        },
    ]


def get_financial_news(
    topic: str = "economy",
    days_back: int = 7,
    max_articles: int = 10,
) -> str:
    """Get recent financial and economic news headlines.

    Use this tool to retrieve current news about economic conditions, market
    sentiment, policy announcements, and financial developments. News provides
    context for understanding emerging trends not yet reflected in official data.

    Args:
        topic: The topic to search for. Suggested topics:
            - 'inflation': News about price increases and CPI
            - 'federal reserve' or 'interest rates': Monetary policy news
            - 'employment' or 'jobs': Labor market news
            - 'economy': General economic news
            - 'stock market': Market performance news
            - 'housing market': Real estate news
            - 'consumer spending': Retail and spending news
            Defaults to 'economy'.
        days_back: Number of days of news to retrieve. Defaults to 7.
        max_articles: Maximum number of articles to return. Defaults to 10.

    Returns:
        A formatted string containing news headlines, sources, dates, and URLs,
        or an error message if the request fails.
    """
    import asyncio

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Add financial context to search
    search_query = f"{topic} finance OR economy OR market"

    from_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    to_date = datetime.now().strftime("%Y-%m-%d")

    result = loop.run_until_complete(
        _fetch_news(
            query=search_query,
            from_date=from_date,
            to_date=to_date,
            page_size=max_articles,
            sort_by="publishedAt",
        )
    )

    if "error" in result and "articles" not in result:
        return f"Error: {result['error']}"

    articles = result.get("articles", [])

    if not articles:
        return f"No recent news found for topic: {topic}"

    lines = [f"Financial News: {topic.title()}"]
    lines.append(f"Retrieved: {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"Showing {len(articles)} articles from the past {days_back} days")
    lines.append("=" * 60)

    for i, article in enumerate(articles, 1):
        title = article.get("title", "No title")
        source = article.get("source", {}).get("name", "Unknown source")
        published = article.get("publishedAt", "")
        url = article.get("url", "")
        description = article.get("description", "")

        # Parse and format date
        if published:
            try:
                pub_date = datetime.fromisoformat(published.replace("Z", "+00:00"))
                published = pub_date.strftime("%Y-%m-%d")
            except ValueError:
                pass

        lines.append(f"\n{i}. {title}")
        lines.append(f"   Source: {source} | Date: {published}")
        if description:
            # Truncate long descriptions
            desc_preview = description[:200] + "..." if len(description) > 200 else description
            lines.append(f"   Summary: {desc_preview}")
        if url:
            lines.append(f"   Link: {url}")

    # Add interpretation guidance
    lines.append("\n" + "=" * 60)
    lines.append("Note: News reflects current sentiment and developments.")
    lines.append("Cross-reference with official data sources for accuracy.")

    return "\n".join(lines)
