"""Database schema. Wipes nothing — only CREATE IF NOT EXISTS.

If you change a table, drop scraper.db and let init_db rebuild it.
This is a diploma project, not a production migration story."""
from app.db.connection import get_conn

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS catalogs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    stats_json TEXT DEFAULT '{}',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_catalogs_user ON catalogs(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS papers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    catalog_id INTEGER NOT NULL,
    doi TEXT,
    title TEXT NOT NULL,
    authors_json TEXT DEFAULT '[]',
    publication_year INTEGER,
    venue TEXT,
    url TEXT,
    abstract TEXT DEFAULT '',
    methodology TEXT DEFAULT '',
    conclusions TEXT DEFAULT '',
    keywords_json TEXT DEFAULT '[]',
    citation_count INTEGER,
    is_open_access INTEGER DEFAULT 0,
    relevance_score REAL DEFAULT 0,
    extraction_source TEXT DEFAULT '',
    failure_reason TEXT DEFAULT 'none',
    language TEXT DEFAULT 'en',
    image_url TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (catalog_id) REFERENCES catalogs(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_papers_catalog ON papers(catalog_id);

CREATE TABLE IF NOT EXISTS research_jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    topic TEXT NOT NULL,
    language TEXT DEFAULT 'en',
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    message TEXT DEFAULT '',
    catalog_id INTEGER,
    error TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now')),
    updated_at TEXT DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (catalog_id) REFERENCES catalogs(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_jobs_user ON research_jobs(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS extraction_cache (
    -- Caches LLM-extracted markdown by (url, schema_hash) so re-runs are free.
    cache_key TEXT PRIMARY KEY,
    url TEXT NOT NULL,
    data_json TEXT NOT NULL,
    markdown_preview TEXT DEFAULT '',
    created_at TEXT DEFAULT (datetime('now'))
);
"""


def init_db() -> None:
    conn = get_conn()
    try:
        conn.executescript(SCHEMA_SQL)
        # Idempotent column additions for upgrades from older DBs.
        _add_column_if_missing(conn, "papers", "image_url", "TEXT DEFAULT ''")
        conn.commit()
    finally:
        conn.close()


def _add_column_if_missing(conn, table: str, column: str, decl: str) -> None:
    cols = {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    if column not in cols:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {decl}")
