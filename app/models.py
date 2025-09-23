from __future__ import annotations

from datetime import datetime, date

from pydantic import BaseModel, HttpUrl, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    time: datetime = Field(default_factory=datetime.utcnow)


class Article(BaseModel):
    title: str
    description: str | None = None
    url: HttpUrl | None = None
    source: str | None = None
    published_at: datetime | None = None
    content: str | None = None


class Summary(BaseModel):
    title: str
    summary: str
    url: HttpUrl | None = None
    source: str | None = None
    published_at: datetime | None = None


class SummarizeRequest(BaseModel):
    text: str
    max_sentences: int = 3


class DigestItem(BaseModel):
    title: str
    summary: str
    url: HttpUrl | None = None
    source: str | None = None
    published_at: datetime | None = None


class Digest(BaseModel):
    date: date
    items: list[DigestItem]
