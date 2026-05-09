"""Catalog → JSON / CSV / BibTeX serializers for export."""
import csv
import io
import re

from app.models.catalog import ScientificCatalog, ScientificPaper


def to_csv(catalog: ScientificCatalog) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow([
        "doi", "title", "authors", "year", "venue", "url", "abstract",
        "methodology", "conclusions", "keywords", "citation_count",
        "is_open_access", "relevance_score", "extraction_source", "failure_reason",
    ])
    for p in catalog.papers:
        w.writerow([
            p.doi or "",
            p.title,
            "; ".join(a.name for a in p.authors),
            p.publication_year or "",
            p.venue or "",
            p.url,
            p.abstract,
            p.methodology,
            p.conclusions,
            "; ".join(p.keywords),
            p.citation_count if p.citation_count is not None else "",
            int(p.is_open_access),
            f"{p.relevance_score:.2f}",
            p.extraction_source,
            p.failure_reason.value if hasattr(p.failure_reason, "value") else str(p.failure_reason),
        ])
    return buf.getvalue()


def to_bibtex(catalog: ScientificCatalog) -> str:
    """Minimal BibTeX export — sufficient for citation managers."""
    chunks = []
    for i, p in enumerate(catalog.papers, start=1):
        key = _bibtex_key(p, i)
        authors = " and ".join(a.name for a in p.authors) or "Anonymous"
        fields = [
            ("title", p.title),
            ("author", authors),
            ("year", str(p.publication_year) if p.publication_year else ""),
            ("journal", p.venue or ""),
            ("doi", p.doi or ""),
            ("url", p.url or ""),
            ("abstract", p.abstract.replace("\n", " ")[:1500]),
            ("keywords", ", ".join(p.keywords)),
        ]
        body = "\n".join(f"  {k} = {{{v}}}," for k, v in fields if v)
        chunks.append(f"@article{{{key},\n{body}\n}}")
    return "\n\n".join(chunks)


def _bibtex_key(p: ScientificPaper, idx: int) -> str:
    last = p.authors[0].name.split()[-1] if p.authors else "anon"
    last = re.sub(r"[^A-Za-z]", "", last) or f"paper{idx}"
    year = p.publication_year or "nd"
    title_word = re.sub(r"[^A-Za-z]+", "", (p.title.split()[0] if p.title else "x"))[:8] or "x"
    return f"{last}{year}{title_word}".lower()
