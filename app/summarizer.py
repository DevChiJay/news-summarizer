from __future__ import annotations

import re
import os

from .config import get_settings


# Split on sentence boundaries followed by whitespace
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
WORD_RE = re.compile(r"[A-Za-z']+")
STOP_WORDS = set(
    """
    a an the and or but if while with to of in on for at by from as is are was were be been being
    it this that these those i you he she they we us them our your his her their my me mine
    not no do does did done can could should would may might will just very more most so than too
    about into over after before between through during without within up down out off again further
    then once here there when where why how all any both each few many some such only own same other
    """.split()
)


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in SENT_SPLIT.split(text.strip()) if s.strip()]


def summarize_text(text: str, max_sentences: int | None = None) -> str:
    settings = get_settings()
    max_sents = max_sentences or settings.summary_sentences

    # Prefer OpenAI if configured via settings or environment
    api_key = getattr(settings, "openai_api_key", None) or os.getenv("OPENAI_API_KEY")
    model = getattr(settings, "openai_model", None) or os.getenv("OPENAI_MODEL") or "gpt-4o-mini"

    if api_key:
        try:
            # Lazy import to avoid hard dependency if not used
            from openai import OpenAI

            client = OpenAI(api_key=api_key)
            user_prompt = (
                f"Summarize the following text in at most {max_sents} sentences. "
                "Keep key facts, names, and numbers. Return only the summary.\n\n"
                f"Text:\n{text}"
            )
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant that produces concise, factual summaries of text and news articles."
                        ),
                    },
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.2,
            )
            content = (resp.choices[0].message.content or "").strip()
            if content:
                return content
        except Exception:
            # If OpenAI call fails for any reason, fall back to the heuristic summarizer below
            pass

    # Fallback: score sentences by word frequency (simple extractive summarizer)
    sentences = split_sentences(text)
    if len(sentences) <= max_sents:
        return text.strip()

    word_freq: dict[str, int] = {}
    for s in sentences:
        for w in WORD_RE.findall(s.lower()):
            if w in STOP_WORDS or len(w) <= 2:
                continue
            word_freq[w] = word_freq.get(w, 0) + 1

    sent_scores: list[tuple[int, float]] = []  # (index, score)
    for idx, s in enumerate(sentences):
        words = [w for w in WORD_RE.findall(s.lower()) if w not in STOP_WORDS and len(w) > 2]
        if not words:
            continue
        score = sum(word_freq.get(w, 0) for w in words) / len(words)
        sent_scores.append((idx, score))

    top = sorted(sent_scores, key=lambda t: t[1], reverse=True)[:max_sents]
    selected_idxs = sorted(i for i, _ in top)
    selected = [sentences[i] for i in selected_idxs]
    return " ".join(selected)
