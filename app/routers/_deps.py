"""Shared dependencies — auth header parsing + user existence check.

The user-existence check matters because the frontend caches the user_id in
localStorage; if scraper.db is recreated the cached id no longer references a
real user, and any DB write that FKs to users(id) crashes. We surface that as
a clean 401 instead, so the client can clear auth and re-login."""
from typing import Optional

from fastapi import Header, HTTPException

from app.db.connection import get_conn


async def require_user(x_user_id: Optional[str] = Header(default=None)) -> int:
    if not x_user_id:
        raise HTTPException(status_code=401, detail="X-User-Id header required")
    try:
        user_id = int(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid X-User-Id")

    conn = get_conn()
    try:
        row = conn.execute("SELECT 1 FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        # Stale session — frontend should clear auth and redirect to /login.
        raise HTTPException(status_code=401, detail="Session expired, please log in again")
    return user_id
