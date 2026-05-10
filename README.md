# LLM-Scraper

Adaptive web scraping with Large Language Models.

A research agent that builds catalogs of scientific literature on any topic. Plus a generic LLM scraping and a comparative benchmark vs. classical methods (trafilatura + BeautifulSoup).

## What it does

1. **Discovery** - queries OpenAlex / Crossref / Semantic Scholar (open science APIs) for a topic, dedupes by DOI.
2. **Relevance filter** - one LLM call ranks all candidates against the topic.
3. **Deep extraction** - Crawl4AI fetches each top paper's open-access URL, converts to markdown, DeepSeek extracts methodology, conclusions, keywords.
4. **Translation (optional)** - separate LLM call renders text fields in Ukrainian.
5. **Persistence** - saves the catalog to SQLite. Export as JSON / CSV / BibTeX.

## Why it's "adaptive"

Classical scrapers use CSS selectors, which break when site layout changes and need per-site configuration. This system extracts clean markdown with Crawl4AI and lets the LLM extract data semantically. One implementation handles arXiv, PubMed Central, publisher pages, university repositories, and any URL the user points it at - without code changes.

## Run locally

You'll need a **DeepSeek API key** (`DEEPSEEK_API_KEY`) for LLM extraction and a
**CORE API key** (`CORE_API_KEY`) for open-access paper URLs. Both are free to get.

```bash
# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill in DEEPSEEK_API_KEY and CORE_API_KEY
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev  # http://localhost:5173
```

Open http://localhost:5173, register an account, and start a research job.

## Project layout

```
app/
  main.py                 FastAPI entry point
  config.py               env vars, model config, pipeline tuning
  models/                 Pydantic schemas (request/response + domain)
    catalog.py            ScientificPaper, ScientificCatalog, ResearchRequest
    discovery.py          DiscoveredPaper (raw API output)
    extraction.py         GenericExtractRequest/Response
    benchmark.py          BenchmarkRequest, ScraperResult, etc.
    jobs.py               ResearchJob status tracking
    auth.py
  routers/                FastAPI routes — thin, no business logic
    auth.py, scrape.py, research.py, catalogs.py, benchmark.py, export.py
  core/                   Generic LLM extraction engine — heart of the diploma
    crawler.py            Crawl4AI wrapper (URL -> markdown)
    llm_extractor.py      Schema-driven extract via DeepSeek-chat
    prompts.py            Prompt templates
  services/
    discovery/            Phase 1 — scientific API clients
      openalex.py, crossref.py, semantic_scholar.py, aggregator.py
    extraction/           Phase 2 — LLM relevance scoring + deep extraction
      relevance.py, paper_extractor.py, translator.py
    pipeline.py           Phase 1 + 2 + Translation orchestration
    generic_extract.py    Service for POST /scrape
    classical_scraper.py  trafilatura+BS4 baseline
    benchmark.py          Side-by-side LLM vs classical
  db/                     SQLite layer
    schema.py, connection.py, users.py, catalogs.py, jobs.py, cache.py
  utils/
    dedupe.py             DOI / title normalization
    exporters.py          JSON / CSV / BibTeX
frontend/                 SvelteKit — Research / Catalogs / Scrape / Benchmark / About
```

## Stack

- **Python + FastAPI** — async backend
- **Crawl4AI** — JS rendering and HTML→markdown conversion
- **DeepSeek-chat** — LLM (\$0.27/\$1.10 per 1M tokens; ~\$0.025 per research query)
- **OpenAlex / Crossref / Semantic Scholar** — open scientific APIs
- **trafilatura + BeautifulSoup** — classical baseline for the benchmark
- **SQLite** — local store for catalogs, jobs, and the URL+schema extraction cache
- **SvelteKit** — frontend with EN/UA i18n
