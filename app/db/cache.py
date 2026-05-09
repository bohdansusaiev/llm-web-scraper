"""LLM extraction cache. Keyed by (url + schema_hash) so changing the schema
busts the cache — but re-running the same query is free."""
import hashlib
import json
from typing import Any, Optional
from app.db.connection import get_conn


def make_cache_key(url: str, schema: Optional[dict[str, Any]], language: str) -> str:
    schema_str = json.dumps(schema, sort_keys=True) if schema else ""
    raw = f"{url}|{language}|{schema_str}"
    return hashlib.sha256(raw.encode()).hexdigest()


def get_cached(cache_key: str) -> Optional[tuple[dict[str, Any], str]]:
    conn = get_conn()
    row = conn.execute(
        "SELECT data_json, markdown_preview FROM extraction_cache WHERE cache_key = ?",
        (cache_key,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    try:
        return json.loads(row["data_json"]), row["markdown_preview"] or ""
    except json.JSONDecodeError:
        return None


def put_cached(cache_key: str, url: str, data: dict[str, Any], markdown_preview: str = "") -> None:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR REPLACE INTO extraction_cache (cache_key, url, data_json, markdown_preview) "
            "VALUES (?, ?, ?, ?)",
            (cache_key, url, json.dumps(data, ensure_ascii=False), markdown_preview[:500]),
        )
        conn.commit()
    finally:
        conn.close()
