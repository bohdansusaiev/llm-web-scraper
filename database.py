import sqlite3
import json
from pathlib import Path

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
        password_hash = _hash_password(password)
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
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()
    if user and _verify_password(password, user["password_hash"]):
        return {"id": user["id"], "username": user["username"]}
    return None


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
