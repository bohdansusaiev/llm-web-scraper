"""Export a catalog as JSON / CSV / BibTeX."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse

from app.db import catalogs as catalogs_db
from app.routers._deps import require_user
from app.utils.exporters import to_csv, to_bibtex

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/{catalog_id}")
async def export_catalog(
    catalog_id: int,
    format: str = "json",
    user_id: int = Depends(require_user),
):
    cat = catalogs_db.get_catalog(catalog_id, user_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catalog not found")
    fmt = format.lower()
    if fmt == "json":
        return JSONResponse(cat.model_dump(mode="json"))
    if fmt == "csv":
        return PlainTextResponse(
            to_csv(cat), media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="catalog_{catalog_id}.csv"'},
        )
    if fmt in ("bib", "bibtex"):
        return PlainTextResponse(
            to_bibtex(cat), media_type="application/x-bibtex",
            headers={"Content-Disposition": f'attachment; filename="catalog_{catalog_id}.bib"'},
        )
    raise HTTPException(status_code=400, detail="format must be json, csv, or bibtex")
