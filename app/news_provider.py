from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import httpx

from .config import get_settings
from .models import Article


NEWSAPI_TOP_HEADLINES_URL = "https://newsapi.org/v2/top-headlines"


async def fetch_top_headlines(country: Optional[str] = None, limit: int = 10) -> list[Article]:
    settings = get_settings()
    country = country or settings.provider_country

    if not settings.news_api_key:
        # Return mock articles
        now = datetime.now(timezone.utc)
        examples = [
            Article(
                title="AI breakthroughs reshape productivity",
                description="Researchers announce new models improving code generation.",
                url="https://example.com/ai-breakthroughs",
                source="ExampleNews",
                published_at=now,
                content=(
                    "Artificial intelligence continues to transform industries. "
                    "New breakthroughs in large language models improve reasoning and coding. "
                    "Experts expect productivity gains across sectors."
                ),
            ),
            Article(
                title="Climate initiatives gather momentum",
                description="Global agreements aim to reduce emissions.",
                url="https://example.com/climate-initiatives",
                source="ExampleNews",
                published_at=now,
                content=(
                    "Nations commit to ambitious climate targets. "
                    "Renewable energy adoption rises as costs fall. "
                    "Businesses invest in sustainable technologies."
                ),
            ),
        ]
        return examples[:limit]

    params = {"apiKey": settings.news_api_key, "country": country, "pageSize": min(limit, 100)}
    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(NEWSAPI_TOP_HEADLINES_URL, params=params)
        resp.raise_for_status()
        data = resp.json()
    articles = []
    for a in data.get("articles", []):
        published = a.get("publishedAt")
        try:
            published_dt = datetime.fromisoformat(published.replace("Z", "+00:00")) if published else None
        except Exception:
            published_dt = None
        articles.append(
            Article(
                title=a.get("title") or "",
                description=a.get("description"),
                url=a.get("url"),
                source=(a.get("source") or {}).get("name"),
                published_at=published_dt,
                content=a.get("content"),
            )
        )
    return articles
