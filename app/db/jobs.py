"""Async research job persistence — the row updated as the pipeline runs."""
from datetime import datetime
from typing import Optional
from app.db.connection import get_conn
from app.models.jobs import ResearchJob, JobStatus


def create_job(user_id: int, topic: str, language: str) -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO research_jobs (user_id, topic, language, status, progress, message) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, topic, language, JobStatus.PENDING.value, 0, "Queued"),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def update_job(
    job_id: int,
    status: Optional[JobStatus] = None,
    progress: Optional[int] = None,
    message: Optional[str] = None,
    catalog_id: Optional[int] = None,
    error: Optional[str] = None,
) -> None:
    fields, values = [], []
    if status is not None:
        fields.append("status = ?")
        values.append(status.value if isinstance(status, JobStatus) else str(status))
    if progress is not None:
        fields.append("progress = ?")
        values.append(progress)
    if message is not None:
        fields.append("message = ?")
        values.append(message)
    if catalog_id is not None:
        fields.append("catalog_id = ?")
        values.append(catalog_id)
    if error is not None:
        fields.append("error = ?")
        values.append(error)
    if not fields:
        return
    fields.append("updated_at = ?")
    values.append(datetime.now().isoformat())
    values.append(job_id)

    conn = get_conn()
    try:
        conn.execute(f"UPDATE research_jobs SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    finally:
        conn.close()


def get_job(job_id: int, user_id: int) -> Optional[ResearchJob]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM research_jobs WHERE id = ? AND user_id = ?",
        (job_id, user_id),
    ).fetchone()
    conn.close()
    if not row:
        return None
    try:
        status = JobStatus(row["status"])
    except ValueError:
        status = JobStatus.PENDING
    return ResearchJob(
        id=row["id"],
        user_id=row["user_id"],
        topic=row["topic"],
        language=row["language"] or "en",
        status=status,
        progress=row["progress"] or 0,
        message=row["message"] or "",
        catalog_id=row["catalog_id"],
        error=row["error"] or "",
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )


def nullify_catalog(catalog_id: int) -> None:
    """Clear catalog_id on jobs that pointed to this catalog (catalog was deleted)."""
    conn = get_conn()
    try:
        conn.execute(
            "UPDATE research_jobs SET catalog_id = NULL WHERE catalog_id = ?",
            (catalog_id,),
        )
        conn.commit()
    finally:
        conn.close()


def list_jobs(user_id: int, limit: int = 20) -> list[ResearchJob]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM research_jobs WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    out = []
    for row in rows:
        try:
            status = JobStatus(row["status"])
        except ValueError:
            status = JobStatus.PENDING
        out.append(ResearchJob(
            id=row["id"],
            user_id=row["user_id"],
            topic=row["topic"],
            language=row["language"] or "en",
            status=status,
            progress=row["progress"] or 0,
            message=row["message"] or "",
            catalog_id=row["catalog_id"],
            error=row["error"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        ))
    return out
