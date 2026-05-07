import sqlite3
import json
from pathlib import Path
from datetime import datetime

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

DB_PATH = Path(__file__).parent / "scraper.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            collection_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            name TEXT DEFAULT '',
            scrape_interval TEXT DEFAULT 'manual'
                CHECK(scrape_interval IN ('manual','hourly','daily','weekly')),
            last_scraped_at TEXT,
            last_status TEXT,
            last_error TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            title TEXT DEFAULT '',
            summary TEXT DEFAULT '',
            article_type TEXT DEFAULT '',
            key_points TEXT DEFAULT '',
            author TEXT DEFAULT '',
            author_url TEXT DEFAULT '',
            date TEXT DEFAULT '',
            image TEXT DEFAULT '',
            translated INTEGER DEFAULT 0,
            language TEXT DEFAULT '',
            scraped_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (source_id) REFERENCES sources(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );

        CREATE TABLE IF NOT EXISTS batch_jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            collection_id INTEGER,
            status TEXT DEFAULT 'pending'
                CHECK(status IN ('pending','running','completed','failed')),
            total INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            failed INTEGER DEFAULT 0,
            results TEXT DEFAULT '[]',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE SET NULL
        );
    """)
    conn.commit()
    conn.close()


def _hash_password(password: str) -> str:
    if HAS_BCRYPT:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    import hashlib
    import secrets
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
    return f"scrypt${salt}${pwd_hash.hex()}"


def _verify_password(password: str, stored: str) -> bool:
    if HAS_BCRYPT and not stored.startswith("scrypt$"):
        try:
            return bcrypt.checkpw(password.encode(), stored.encode())
        except Exception:
            return False
    if stored.startswith("scrypt$"):
        import hashlib
        _, salt, pwd_hash = stored.split("$")
        result = hashlib.scrypt(password.encode(), salt=salt.encode(), n=16384, r=8, p=1, dklen=64)
        return result.hex() == pwd_hash
    return False


def register_user(username: str, password: str) -> bool:
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, _hash_password(password)),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username: str, password: str):
    conn = get_conn()
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    if user and _verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return None


def get_collections(user_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT c.*, "
        "(SELECT COUNT(*) FROM sources s WHERE s.collection_id = c.id) as source_count, "
        "(SELECT COUNT(*) FROM articles a "
        " JOIN sources s ON a.source_id = s.id "
        " WHERE s.collection_id = c.id) as article_count "
        "FROM collections c WHERE c.user_id = ? ORDER BY c.created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_collection(user_id: int, name: str):
    conn = get_conn()
    conn.execute(
        "INSERT INTO collections (user_id, name) VALUES (?, ?)",
        (user_id, name),
    )
    conn.commit()
    conn.close()


def delete_collection(collection_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM collections WHERE id = ?", (collection_id,))
    conn.commit()
    conn.close()


def get_sources(collection_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT s.*, "
        "(SELECT COUNT(*) FROM articles a WHERE a.source_id = s.id) as article_count "
        "FROM sources s WHERE s.collection_id = ? ORDER BY s.created_at DESC",
        (collection_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_source(source_id: int):
    conn = get_conn()
    row = conn.execute(
        "SELECT s.*, "
        "(SELECT COUNT(*) FROM articles a WHERE a.source_id = s.id) as article_count "
        "FROM sources s WHERE s.id = ?",
        (source_id,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def create_source(collection_id: int, url: str, name: str = "", scrape_interval: str = "manual"):
    conn = get_conn()
    conn.execute(
        "INSERT INTO sources (collection_id, url, name, scrape_interval) VALUES (?, ?, ?, ?)",
        (collection_id, url, name, scrape_interval),
    )
    conn.commit()
    conn.close()


def update_source(source_id: int, name: str = None, scrape_interval: str = None):
    conn = get_conn()
    fields = []
    values = []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if scrape_interval is not None:
        fields.append("scrape_interval = ?")
        values.append(scrape_interval)
    if fields:
        values.append(source_id)
        conn.execute(
            f"UPDATE sources SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
    conn.close()


def delete_source(source_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    conn.commit()
    conn.close()


def save_article(user_id: int, url: str, data: dict, source_id: int = None):
    conn = get_conn()
    conn.execute(
        "INSERT INTO articles (source_id, user_id, url, title, summary, article_type, "
        "key_points, author, author_url, date, image, translated, language) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
        (
            source_id,
            user_id,
            url,
            data.get("title", ""),
            data.get("summary", ""),
            data.get("article_type", ""),
            data.get("key_points", ""),
            data.get("author", ""),
            data.get("author_url", ""),
            data.get("date", ""),
            data.get("image", ""),
            1 if data.get("translated") else 0,
            data.get("language", ""),
        ),
    )
    conn.commit()
    conn.close()


def save_history(user_id: int, url: str, data: dict, source_id: int = None):
    return save_article(user_id, url, data, source_id=source_id)


def get_history(user_id: int):
    return get_articles(user_id, limit=100)


def get_articles(
    user_id: int,
    collection_id: int = None,
    source_id: int = None,
    article_type: str = None,
    search_query: str = None,
    limit: int = 50,
    offset: int = 0,
):
    conn = get_conn()
    conditions = ["a.user_id = ?"]
    params = [user_id]

    if collection_id:
        conditions.append("s.collection_id = ?")
        params.append(collection_id)
    if source_id:
        conditions.append("a.source_id = ?")
        params.append(source_id)
    if article_type:
        conditions.append("a.article_type = ?")
        params.append(article_type)
    if search_query:
        conditions.append(
            "(a.title LIKE ? OR a.summary LIKE ? OR a.author LIKE ? OR a.key_points LIKE ?)"
        )
        q = f"%{search_query}%"
        params.extend([q, q, q, q])

    where = " AND ".join(conditions)

    rows = conn.execute(
        f"SELECT a.*, s.name as source_name, s.collection_id "
        f"FROM articles a "
        f"LEFT JOIN sources s ON a.source_id = s.id "
        f"WHERE {where} "
        f"ORDER BY a.scraped_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset],
    ).fetchall()

    conn.close()
    return [dict(r) for r in rows]


def get_article_count(user_id: int, collection_id: int = None):
    conn = get_conn()
    if collection_id:
        count = conn.execute(
            "SELECT COUNT(*) FROM articles a "
            "JOIN sources s ON a.source_id = s.id "
            "WHERE a.user_id = ? AND s.collection_id = ?",
            (user_id, collection_id),
        ).fetchone()[0]
    else:
        count = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE user_id = ?",
            (user_id,),
        ).fetchone()[0]
    conn.close()
    return count


def get_articles_for_export(user_id: int, collection_id: int = None, article_ids: list = None):
    conn = get_conn()
    conditions = ["a.user_id = ?"]
    params = [user_id]

    if collection_id:
        conditions.append("s.collection_id = ?")
        params.append(collection_id)
    if article_ids:
        placeholders = ",".join("?" for _ in article_ids)
        conditions.append(f"a.id IN ({placeholders})")
        params.extend(article_ids)

    where = " AND ".join(conditions)
    rows = conn.execute(
        f"SELECT a.*, s.name as source_name, c.name as collection_name "
        f"FROM articles a "
        f"LEFT JOIN sources s ON a.source_id = s.id "
        f"LEFT JOIN collections c ON s.collection_id = c.id "
        f"WHERE {where} ORDER BY a.scraped_at DESC",
        params,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_article(article_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM articles WHERE id = ?", (article_id,))
    conn.commit()
    conn.close()


def create_batch_job(user_id: int, collection_id: int, total: int):
    conn = get_conn()
    conn.execute(
        "INSERT INTO batch_jobs (user_id, collection_id, total) VALUES (?, ?, ?)",
        (user_id, collection_id, total),
    )
    conn.commit()
    job_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.close()
    return job_id


def update_batch_job(job_id: int, **kwargs):
    conn = get_conn()
    fields = []
    values = []
    for key, val in kwargs.items():
        if val is not None:
            fields.append(f"{key} = ?")
            values.append(val)
    if fields:
        values.append(job_id)
        conn.execute(
            f"UPDATE batch_jobs SET {', '.join(fields)} WHERE id = ?",
            values,
        )
        conn.commit()
    conn.close()


def get_batch_job(job_id: int):
    conn = get_conn()
    row = conn.execute("SELECT * FROM batch_jobs WHERE id = ?", (job_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def get_due_sources():
    conn = get_conn()
    rows = conn.execute(
        "SELECT s.*, c.user_id FROM sources s "
        "JOIN collections c ON s.collection_id = c.id "
        "WHERE s.scrape_interval != 'manual' "
        "AND (s.last_scraped_at IS NULL OR "
        "  (s.scrape_interval = 'hourly' AND datetime(s.last_scraped_at, '+1 hour') <= datetime('now')) OR "
        "  (s.scrape_interval = 'daily' AND datetime(s.last_scraped_at, '+1 day') <= datetime('now')) OR "
        "  (s.scrape_interval = 'weekly' AND datetime(s.last_scraped_at, '+7 days') <= datetime('now'))"
        ")"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_source_status(source_id: int, status: str, scraped_at: str = None, error: str = None):
    conn = get_conn()
    if scraped_at:
        conn.execute(
            "UPDATE sources SET last_status = ?, last_scraped_at = ?, last_error = ? WHERE id = ?",
            (status, scraped_at, error, source_id),
        )
    else:
        conn.execute(
            "UPDATE sources SET last_status = ?, last_error = ? WHERE id = ?",
            (status, error, source_id),
        )
    conn.commit()
    conn.close()
