from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Optional

from .config import get_settings
from .models import Digest


def daily_digest_path(d: date) -> Path:
    s = get_settings()
    return s.daily_dir / f"digest_{d.isoformat()}.json"


def save_digest(digest: Digest) -> Path:
    path = daily_digest_path(digest.date)
    with path.open("w", encoding="utf-8") as f:
        json.dump(digest.model_dump(), f, ensure_ascii=False, indent=2, default=str)
    return path


def load_digest(d: date) -> Digest | None:
    path = daily_digest_path(d)
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return Digest(**data)
