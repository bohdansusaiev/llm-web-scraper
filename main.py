import asyncio
import json
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from scraper import scrape_article
from database import (
    init_db,
    register_user as db_register_user,
    login_user as db_login_user,
    get_collections, create_collection, delete_collection,
    get_sources, get_source, create_source, update_source, delete_source,
    save_article, get_articles, get_article_count,
    get_history, create_batch_job, update_batch_job, get_batch_job,
    update_source_status,
    get_articles_for_export, delete_article,
)
from scheduler import scheduler_loop


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    task = asyncio.create_task(scheduler_loop())
    yield
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="NewsScraper API",
    description="Adaptive news article extraction using LLMs",
    version="3.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def _require_user(x_user_id: Optional[str] = Header(None)):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        return int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id")


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str


class ScrapeRequest(BaseModel):
    url: str
    language: str = "en"
    source_id: Optional[int] = None


class BatchScrapeRequest(BaseModel):
    collection_id: int
    language: str = "en"


@app.get("/")
async def root():
    return {"status": "ok", "version": "3.0.0"}


@app.post("/auth/register")
async def register_endpoint(request: RegisterRequest):
    ok = db_register_user(request.username, request.password)
    if not ok:
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"status": "ok"}


@app.post("/auth/login")
async def login_endpoint(request: LoginRequest):
    user = db_login_user(request.username, request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@app.post("/scrape")
async def scrape_endpoint(request: ScrapeRequest, x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    try:
        result = await scrape_article(request.url, request.language)
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        article_id = save_article(user_id, request.url, result, source_id=request.source_id)
        return {"id": article_id, **result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scrape/batch")
async def batch_scrape(request: BatchScrapeRequest, x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    sources = get_sources(request.collection_id)
    if not sources:
        raise HTTPException(status_code=400, detail="No sources in this collection")

    job_id = create_batch_job(user_id, request.collection_id, len(sources))
    update_batch_job(job_id, status="running")

    asyncio.create_task(_run_batch(job_id, sources, user_id, request.language))

    return {"job_id": job_id, "total": len(sources)}


async def _run_batch(job_id: int, sources: list, user_id: int, language: str):
    completed = 0
    failed = 0
    results = []
    for source in sources:
        try:
            result = await scrape_article(source["url"], language)
            if result.get("error"):
                failed += 1
                update_source_status(source["id"], "error", error=result["error"])
            else:
                save_article(user_id, source["url"], result, source_id=source["id"])
                update_source_status(source["id"], "ok", scraped_at=datetime.now().isoformat())
                completed += 1
                results.append({"source_id": source["id"], "url": source["url"], "status": "ok"})
        except Exception as e:
            failed += 1
            update_source_status(source["id"], "error", error=str(e))
            results.append({"source_id": source["id"], "url": source["url"], "status": "error", "error": str(e)})
        update_batch_job(job_id, completed=completed, failed=failed, results=json.dumps(results, ensure_ascii=False))
    update_batch_job(job_id, status="completed", completed=completed, failed=failed, results=json.dumps(results, ensure_ascii=False))


@app.get("/scrape/batch/{job_id}")
async def get_batch_status(job_id: int):
    job = get_batch_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    job["results"] = json.loads(job["results"]) if isinstance(job["results"], str) else job["results"]
    return job


@app.get("/collections")
async def list_collections(x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    return get_collections(user_id)


@app.post("/collections")
async def add_collection(name: str, x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    create_collection(user_id, name)
    return {"status": "ok"}


@app.delete("/collections/{collection_id}")
async def remove_collection(collection_id: int, x_user_id: Optional[str] = Header(None)):
    await _require_user(x_user_id)
    delete_collection(collection_id)
    return {"status": "ok"}


@app.get("/collections/{collection_id}/sources")
async def list_sources(collection_id: int, x_user_id: Optional[str] = Header(None)):
    await _require_user(x_user_id)
    return get_sources(collection_id)


@app.post("/collections/{collection_id}/sources")
async def add_source(
    collection_id: int,
    url: str,
    name: str = "",
    scrape_interval: str = "manual",
    x_user_id: Optional[str] = Header(None),
):
    await _require_user(x_user_id)
    create_source(collection_id, url, name, scrape_interval)
    return {"status": "ok"}


@app.get("/sources/{source_id}")
async def get_source_endpoint(source_id: int, x_user_id: Optional[str] = Header(None)):
    await _require_user(x_user_id)
    source = get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


@app.put("/sources/{source_id}")
async def edit_source(
    source_id: int,
    name: str = None,
    scrape_interval: str = None,
    x_user_id: Optional[str] = Header(None),
):
    await _require_user(x_user_id)
    update_source(source_id, name, scrape_interval)
    return {"status": "ok"}


@app.delete("/sources/{source_id}")
async def remove_source(source_id: int, x_user_id: Optional[str] = Header(None)):
    await _require_user(x_user_id)
    delete_source(source_id)
    return {"status": "ok"}


@app.post("/sources/{source_id}/scrape")
async def scrape_source(source_id: int, x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    source = get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    try:
        result = await scrape_article(source["url"])
        if result.get("error"):
            update_source_status(source_id, "error", error=result["error"])
            raise HTTPException(status_code=500, detail=result["error"])
        article_id = save_article(user_id, source["url"], result, source_id=source_id)
        update_source_status(source_id, "ok", scraped_at=datetime.now().isoformat())
        return {"id": article_id, **result}
    except HTTPException:
        raise
    except Exception as e:
        update_source_status(source_id, "error", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/articles")
async def list_articles(
    collection_id: Optional[int] = None,
    source_id: Optional[int] = None,
    article_type: Optional[str] = None,
    q: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    x_user_id: Optional[str] = Header(None),
):
    user_id = await _require_user(x_user_id)
    articles = get_articles(
        user_id=user_id,
        collection_id=collection_id,
        source_id=source_id,
        article_type=article_type,
        search_query=q,
        limit=limit,
        offset=offset,
    )
    for a in articles:
        a["translated"] = bool(a["translated"])
    return articles


@app.get("/articles/count")
async def articles_count(
    collection_id: Optional[int] = None,
    x_user_id: Optional[str] = Header(None),
):
    user_id = await _require_user(x_user_id)
    return {"count": get_article_count(user_id, collection_id)}


@app.delete("/articles/{article_id}")
async def remove_article(article_id: int, x_user_id: Optional[str] = Header(None)):
    await _require_user(x_user_id)
    delete_article(article_id)
    return {"status": "ok"}


@app.get("/history")
async def list_history(limit: int = 50, x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    articles = get_history(user_id)
    for a in articles:
        a["translated"] = bool(a["translated"])
    return articles[:limit]


@app.get("/export")
async def export_articles(
    format: str = "json",
    collection_id: Optional[int] = None,
    article_ids: Optional[str] = None,
    x_user_id: Optional[str] = Header(None),
):
    user_id = await _require_user(x_user_id)
    ids = [int(i) for i in article_ids.split(",")] if article_ids else None
    articles = get_articles_for_export(user_id, collection_id, ids)

    if format == "json":
        return articles
    elif format == "csv":
        import csv
        import io
        buf = io.StringIO()
        w = csv.writer(buf)
        w.writerow(["id", "url", "title", "summary", "article_type", "key_points",
                     "author", "author_url", "date", "image", "translated",
                     "scraped_at", "source_name", "collection_name"])
        for a in articles:
            w.writerow([a["id"], a["url"], a["title"], a["summary"], a["article_type"],
                       a["key_points"], a["author"], a["author_url"], a["date"],
                       a["image"], a["translated"], a["scraped_at"],
                       a.get("source_name", ""), a.get("collection_name", "")])
        return {"csv": buf.getvalue()}
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")


@app.get("/dashboard/stats")
async def dashboard_stats(x_user_id: Optional[str] = Header(None)):
    user_id = await _require_user(x_user_id)
    from database import get_conn
    conn = get_conn()
    total_articles = conn.execute(
        "SELECT COUNT(*) FROM articles WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    total_collections = conn.execute(
        "SELECT COUNT(*) FROM collections WHERE user_id = ?", (user_id,)
    ).fetchone()[0]
    total_sources = conn.execute(
        "SELECT COUNT(*) FROM sources s JOIN collections c ON s.collection_id = c.id WHERE c.user_id = ?",
        (user_id,),
    ).fetchone()[0]
    type_counts = conn.execute(
        "SELECT article_type, COUNT(*) as cnt FROM articles "
        "WHERE user_id = ? AND article_type != '' "
        "GROUP BY article_type ORDER BY cnt DESC",
        (user_id,),
    ).fetchall()
    overdue = conn.execute(
        "SELECT s.*, c.name as collection_name FROM sources s "
        "JOIN collections c ON s.collection_id = c.id "
        "WHERE c.user_id = ? AND s.scrape_interval != 'manual' "
        "AND (s.last_scraped_at IS NULL OR "
        "  (s.scrape_interval = 'hourly' AND datetime(s.last_scraped_at, '+1 hour') <= datetime('now')) OR "
        "  (s.scrape_interval = 'daily' AND datetime(s.last_scraped_at, '+1 day') <= datetime('now')) OR "
        "  (s.scrape_interval = 'weekly' AND datetime(s.last_scraped_at, '+7 days') <= datetime('now'))"
        ")",
        (user_id,),
    ).fetchall()
    conn.close()
    return {
        "total_articles": total_articles,
        "total_collections": total_collections,
        "total_sources": total_sources,
        "type_counts": [dict(t) for t in type_counts],
        "overdue": [dict(o) for o in overdue],
    }
