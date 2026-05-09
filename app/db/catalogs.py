"""Persist scientific catalogs and their papers."""
import json
from datetime import datetime
from typing import Optional
from app.db.connection import get_conn
from app.models.catalog import (
    ScientificCatalog, ScientificPaper, CatalogStats, CatalogSummary,
    Author, ExtractionFailureReason,
)


def save_catalog(user_id: int, catalog: ScientificCatalog) -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO catalogs (user_id, topic, language, stats_json) VALUES (?, ?, ?, ?)",
            (user_id, catalog.topic, catalog.language, catalog.stats.model_dump_json()),
        )
        catalog_id = cur.lastrowid

        for p in catalog.papers:
            conn.execute(
                """INSERT INTO papers (
                    catalog_id, doi, title, authors_json, publication_year, venue, url,
                    abstract, methodology, conclusions, keywords_json, citation_count,
                    is_open_access, relevance_score, extraction_source, failure_reason,
                    language, image_url
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    catalog_id, p.doi, p.title,
                    json.dumps([a.model_dump() for a in p.authors], ensure_ascii=False),
                    p.publication_year, p.venue, p.url,
                    p.abstract, p.methodology, p.conclusions,
                    json.dumps(p.keywords, ensure_ascii=False),
                    p.citation_count,
                    1 if p.is_open_access else 0,
                    p.relevance_score, p.extraction_source,
                    p.failure_reason.value if isinstance(p.failure_reason, ExtractionFailureReason)
                        else str(p.failure_reason),
                    p.language,
                    p.image_url or "",
                ),
            )
        conn.commit()
        return catalog_id
    finally:
        conn.close()


def list_catalogs(user_id: int) -> list[CatalogSummary]:
    conn = get_conn()
    rows = conn.execute(
        """SELECT c.id, c.topic, c.language, c.created_at,
           (SELECT COUNT(*) FROM papers p WHERE p.catalog_id = c.id) AS paper_count
           FROM catalogs c WHERE c.user_id = ? ORDER BY c.created_at DESC""",
        (user_id,),
    ).fetchall()
    conn.close()
    return [
        CatalogSummary(
            id=r["id"], topic=r["topic"], language=r["language"],
            created_at=datetime.fromisoformat(r["created_at"]),
            paper_count=r["paper_count"],
        )
        for r in rows
    ]


def get_catalog(catalog_id: int, user_id: int) -> Optional[ScientificCatalog]:
    conn = get_conn()
    cat = conn.execute(
        "SELECT * FROM catalogs WHERE id = ? AND user_id = ?",
        (catalog_id, user_id),
    ).fetchone()
    if not cat:
        conn.close()
        return None
    paper_rows = conn.execute(
        "SELECT * FROM papers WHERE catalog_id = ? ORDER BY relevance_score DESC, id ASC",
        (catalog_id,),
    ).fetchall()
    conn.close()

    papers = [_row_to_paper(r) for r in paper_rows]
    stats = CatalogStats.model_validate_json(cat["stats_json"]) if cat["stats_json"] else CatalogStats()
    return ScientificCatalog(
        id=cat["id"],
        user_id=cat["user_id"],
        topic=cat["topic"],
        language=cat["language"],
        created_at=datetime.fromisoformat(cat["created_at"]),
        papers=papers,
        stats=stats,
    )


def delete_catalog(catalog_id: int, user_id: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute(
            "DELETE FROM catalogs WHERE id = ? AND user_id = ?",
            (catalog_id, user_id),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def _row_to_paper(r) -> ScientificPaper:
    authors_data = json.loads(r["authors_json"]) if r["authors_json"] else []
    authors = [Author(**a) if isinstance(a, dict) else Author(name=str(a)) for a in authors_data]
    keywords = json.loads(r["keywords_json"]) if r["keywords_json"] else []
    try:
        failure = ExtractionFailureReason(r["failure_reason"])
    except (ValueError, KeyError):
        failure = ExtractionFailureReason.NONE
    image_url = ""
    try:
        image_url = r["image_url"] or ""
    except (IndexError, KeyError):
        pass  # older DBs without the column
    return ScientificPaper(
        doi=r["doi"],
        title=r["title"],
        authors=authors,
        publication_year=r["publication_year"],
        venue=r["venue"],
        url=r["url"] or "",
        abstract=r["abstract"] or "",
        methodology=r["methodology"] or "",
        conclusions=r["conclusions"] or "",
        keywords=keywords,
        image_url=image_url,
        citation_count=r["citation_count"],
        is_open_access=bool(r["is_open_access"]),
        relevance_score=r["relevance_score"] or 0.0,
        extraction_source=r["extraction_source"] or "",
        failure_reason=failure,
        language=r["language"] or "en",
    )
