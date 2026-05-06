import sqlite3
import hashlib
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "scraper.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
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
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            url TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()


def register_user(username: str, password: str) -> bool:
    conn = get_conn()
    try:
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username: str, password: str):
    conn = get_conn()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = conn.execute(
        "SELECT id, username FROM users WHERE username = ? AND password_hash = ?",
        (username, password_hash),
    ).fetchone()
    conn.close()
    return dict(user) if user else None


def save_history(user_id: int, url: str, result: dict):
    conn = get_conn()
    conn.execute(
        "INSERT INTO history (user_id, url, result) VALUES (?, ?, ?)",
        (user_id, url, json.dumps(result, ensure_ascii=False)),
    )
    conn.commit()
    conn.close()


def get_history(user_id: int):
    conn = get_conn()
    rows = conn.execute(
        "SELECT id, url, result, created_at FROM history "
        "WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
