# News Summarizer API

A lightweight FastAPI service that fetches top headlines, summarizes content, and generates a daily digest via a scheduler. Includes OpenAPI docs for testing and a Dockerfile for deployment.

## Features
- Top headlines endpoint (uses NewsAPI if `NEWS_API_KEY` is set; otherwise returns mock data)
- Text summarization endpoint
- Daily digest generator (scheduled job) with storage as JSON under `data/daily`
- OpenAPI docs for quick testing
- Dockerfile for containerized deployment

## Setup

### Local (Python 3.11+)
1. Create and activate a virtual env (optional but recommended).
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Copy environment example and edit if needed:
   - `cp .env.example .env`
4. Run the app (choose one):
   - `uvicorn main:app --reload`  # direct Uvicorn
   - `fastapi dev main.py`        # FastAPI CLI with reload and nice errors (install fastapi-cli or fastapi[standard])
5. Open API docs: http://127.0.0.1:8000/docs

### Docker
1. Build image:
   - `docker build -t news-summarizer .`
2. Run container:
   - `docker run -p 8000:8000 --env-file .env -v %cd%/data:/app/data news-summarizer`

## Endpoints (docs)
- GET `/health` — service health
- GET `/news/top?country=us&limit=10` — top headlines
- POST `/summarize` — summarize arbitrary text
- GET `/digest/today` — returns today's digest, generating if missing
- GET `/digest/YYYY-MM-DD` — returns digest for a specific date

### Example request for /summarize
```
{
  "text": "Artificial intelligence continues to transform industries. New breakthroughs in large language models improve reasoning and coding. Experts expect productivity gains across sectors.",
  "max_sentences": 2
}
```

## Environment variables
- `NEWS_API_KEY` (optional): Key for NewsAPI.org. If missing, mock headlines are used.
- `DAILY_DIGEST_TIME` (optional): HH:MM (24-hour) for when the digest job runs. Default `07:00`.
- `SUMMARY_SENTENCES` (optional): Default number of sentences in summary. Default `3`.
- `PROVIDER_COUNTRY` (optional): Two-letter country code for headlines. Default `us`.

## Notes
- The scheduled job uses APScheduler and starts with the app. In development with `--reload`, the scheduler may start twice if not guarded by a single-process runner. Use without `--reload` in production.
- All digests are written to `data/daily` as `digest_YYYY-MM-DD.json`.