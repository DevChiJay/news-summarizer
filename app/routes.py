from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from .models import Article, Digest, HealthResponse, SummarizeRequest, Summary
from .news_provider import fetch_top_headlines
from .scheduler import generate_daily_digest
from .storage import load_digest
from .summarizer import summarize_text


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["system"])
async def health() -> HealthResponse:
    return HealthResponse()


@router.get("/news/top", response_model=list[Article], tags=["news"])
async def top_news(
    country: Annotated[str | None, Query(description="ISO country code, e.g., 'us'")] = None,
    limit: Annotated[int, Query(gt=0, le=100)] = 10,
) -> list[Article]:
    return await fetch_top_headlines(country=country, limit=limit)


@router.post("/summarize", response_model=Summary, tags=["summarize"], summary="Summarize text using OpenAI (with fallback)")
async def summarize(req: SummarizeRequest) -> Summary:
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="text is required")
    summary_text = summarize_text(req.text, max_sentences=req.max_sentences)
    return Summary(title=req.text[:60], summary=summary_text)


@router.get(
    	"/digest/today",
    	response_model=Digest,
    	tags=["digest"],
    	summary="Get today's digest, generating if missing",
)
async def today_digest() -> Digest:
    d = date.today()
    existing = load_digest(d)
    if existing:
        return existing
    # Generate on-demand if missing
    return await generate_daily_digest()


@router.get(
    	"/digest/{yyyy}-{mm}-{dd}",
    	response_model=Digest,
    	tags=["digest"],
    	summary="Get a specific day's digest",
)
async def specific_digest(yyyy: int, mm: int, dd: int) -> Digest:
    try:
        d = date(yyyy, mm, dd)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date")
    existing = load_digest(d)
    if not existing:
        raise HTTPException(status_code=404, detail="Digest not found")
    return existing
