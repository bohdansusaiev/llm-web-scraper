# LLM-Scraper

Bachelor's diploma project: **adaptive web scraping with Large Language Models**.

A research agent that builds catalogs of scientific literature on any topic.
Plus a generic LLM scraping endpoint and a comparative benchmark vs. classical
methods (trafilatura + BeautifulSoup).

## What it does

1. **Discovery** — queries OpenAlex / Crossref / Semantic Scholar (open science APIs) for a topic, dedupes by DOI.
2. **Relevance filter** — one LLM call ranks all candidates against the topic.
3. **Deep extraction** — Crawl4AI fetches each top paper's open-access URL → markdown → DeepSeek extracts methodology, conclusions, keywords.
4. **Translation (optional)** — separate LLM call renders text fields in Ukrainian.
5. **Persistence** — saves the catalog to SQLite. Export as JSON / CSV / BibTeX.

The same engine is exposed at `POST /scrape` — pass any URL + JSON schema and
the LLM returns structured data.

## Why it's "adaptive"

Classical scrapers rely on CSS selectors. They break the moment a site redesigns,
and you need a separate config for every domain. This project takes a different
approach: Crawl4AI renders the page and converts it to clean markdown, then
DeepSeek reads that markdown and extracts whatever fields you ask for.

The result is that **one implementation works on arXiv, PubMed Central, journal
pages, university repositories, and anything else** — without touching the code.
If the site changes its layout, nothing breaks. If you point it at a completely
new domain, it just works.

The `POST /benchmark` endpoint makes this concrete: classical extraction typically
recovers 4–5 out of 9 fields with broken author parsing, while LLM extraction
gets 8–9 including methodology and conclusions that pattern matching can't reach.

## Running locally

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in DEEPSEEK_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev   # → http://localhost:5173
```

Register an account, pick a research topic, and the pipeline runs in the
background while you watch the progress bar.

## How the code is organized

The backend is split by responsibility rather than by feature, so it's easier
to follow each phase of the pipeline separately.

```
app/
  core/                   The main idea — URL → markdown → structured data
    crawler.py            Crawl4AI wrapper, falls back to Jina Reader if needed
    llm_extractor.py      Schema-driven extraction via DeepSeek-chat
    prompts.py            All prompt templates in one place

  services/
    discovery/            Phase 1 — pull candidates from scientific APIs
      openalex.py, semantic_scholar.py, arxiv.py, core.py, crossref.py
      aggregator.py       runs them in parallel, dedupes by DOI
    extraction/           Phase 2 — filter and extract
      relevance.py        LLM scores each paper 0–10 against the topic
      paper_extractor.py  deep extraction for papers that pass the filter
      translator.py       optional Ukrainian translation pass
    pipeline.py           wires Phase 1 + 2 + translation into one job
    generic_extract.py    the POST /scrape service
    classical_scraper.py  trafilatura + BeautifulSoup baseline
    benchmark.py          runs both and formats the comparison

  routers/                thin HTTP layer — no business logic here
  models/                 Pydantic schemas
  db/                     SQLite (catalogs, jobs, users, extraction cache)
  utils/
    dedupe.py             normalizes DOIs and titles before deduplication
    exporters.py          JSON / CSV / BibTeX writers

frontend/                 SvelteKit app — Research, Catalogs, Scrape, Benchmark, About
```

## API

| Method | Path | What it does |
|---|---|---|
| `POST` | `/auth/register`, `/auth/login` | create account / get user id |
| `POST` | `/research` | start a pipeline job, returns `{job_id}` |
| `GET`  | `/research/{job_id}` | poll progress and result |
| `GET`  | `/catalogs` | list saved catalogs |
| `GET`  | `/catalogs/{id}` | full catalog with all papers |
| `DELETE` | `/catalogs/{id}` | delete it |
| `GET`  | `/export/{id}?format=json\|csv\|bibtex` | download catalog |
| `POST` | `/scrape` | extract structured data from any URL |
| `POST` | `/benchmark` | compare LLM vs classical on one URL |
| `POST` | `/benchmark/batch` | same, across multiple URLs |

Authenticated endpoints use `X-User-Id: <id>` (returned by `/auth/login`).

## Stack

- **FastAPI** — async Python backend
- **Crawl4AI + Jina Reader** — JS-rendered page → clean markdown (Jina as fallback)
- **DeepSeek-chat** — cheap and capable (~$0.025 per full research job)
- **OpenAlex / Semantic Scholar / arXiv / CORE** — open-access scientific APIs
- **trafilatura + BeautifulSoup** — classical baseline for the benchmark
- **SQLite** — stores catalogs, job queue, and a URL+schema extraction cache
- **SvelteKit** — frontend with EN/UA i18n, dark/light theme

## Author

Bohdan Susaiev
