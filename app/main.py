"""FastAPI entry point. Run with: uvicorn app.main:app --reload"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.schema import init_db
from app.routers import auth, scrape, research, catalogs, benchmark, export

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    logger.info("DB initialized; app ready.")
    yield


app = FastAPI(
    title="LLM-Scraper",
    description=(
        "Adaptive web scraping with Large Language Models. "
        "Scientific literature catalog generation as the headline application, "
        "plus a generic /scrape endpoint and an LLM-vs-classical benchmark."
    ),
    version="4.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(scrape.router)
app.include_router(research.router)
app.include_router(catalogs.router)
app.include_router(benchmark.router)
app.include_router(export.router)


@app.get("/", tags=["meta"])
async def root() -> dict:
    return {
        "name": "LLM-Scraper",
        "version": "4.0.0",
        "endpoints": [
            "POST /auth/register", "POST /auth/login",
            "POST /scrape (generic LLM extraction)",
            "POST /research (start a topic-based research job)",
            "GET  /research/{job_id} (poll job status + catalog)",
            "GET  /catalogs (list saved catalogs)",
            "GET  /catalogs/{id}",
            "POST /benchmark (LLM vs classical, single URL)",
            "POST /benchmark/batch (LLM vs classical across many URLs)",
            "GET  /export/{catalog_id}?format=json|csv|bibtex",
        ],
    }
