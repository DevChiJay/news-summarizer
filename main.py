from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.routes import router
from app.scheduler import start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
	# Startup
	app.state.scheduler = start_scheduler()
	try:
		yield
	finally:
		# Shutdown
		sched = getattr(app.state, "scheduler", None)
		if sched:
			sched.shutdown(wait=False)


settings = get_settings()
app = FastAPI(
	title=settings.app_name,
	version="0.1.0",
	description=(
		"A simple News Summarizer API. Fetch top headlines, summarize text, and get a daily digest."
	),
	lifespan=lifespan,
)

app.include_router(router)


# Optional: allow `python main.py` to run a local dev server if uvicorn installed
if __name__ == "__main__":  # pragma: no cover
	try:
		import uvicorn

		uvicorn.run(
			"main:app",
			host="0.0.0.0",
			port=8000,
			reload=True,
			log_level="info",
		)
	except Exception as exc:
		print("Failed to start uvicorn:", exc)
