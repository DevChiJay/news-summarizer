from __future__ import annotations

from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from .config import get_settings
from .models import Digest, DigestItem
from .news_provider import fetch_top_headlines
from .storage import save_digest
from .summarizer import summarize_text


async def generate_daily_digest() -> Digest:
    settings = get_settings()
    articles = await fetch_top_headlines(limit=10)
    items: list[DigestItem] = []
    for a in articles:
        text = a.content or a.description or a.title
        summary = summarize_text(text, max_sentences=settings.summary_sentences)
        items.append(
            DigestItem(
                title=a.title,
                summary=summary,
                url=a.url,
                source=a.source,
                published_at=a.published_at,
            )
        )
    digest = Digest(date=date.today(), items=items)
    save_digest(digest)
    return digest


def start_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler = AsyncIOScheduler()
    hour, minute = (int(x) for x in settings.daily_digest_time.split(":", 1))
    scheduler.add_job(generate_daily_digest, CronTrigger(hour=hour, minute=minute))
    scheduler.start()
    return scheduler
