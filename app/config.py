from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DAILY_DIR = DATA_DIR / "daily"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(BASE_DIR / ".env"), env_file_encoding="utf-8", extra="ignore")

    app_name: str = "News Summarizer API"
    environment: str = "development"
    news_api_key: Optional[str] = None
    daily_digest_time: str = "07:00"  # HH:MM 24h local time
    summary_sentences: int = 3
    provider_country: str = "us"

    # Storage
    data_dir: Path = DATA_DIR
    daily_dir: Path = DAILY_DIR


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.daily_dir.mkdir(parents=True, exist_ok=True)
    return settings
