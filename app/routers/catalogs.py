"""Catalog browsing — list, fetch, delete saved scientific catalogs."""
from fastapi import APIRouter, Depends, HTTPException

from app.db import catalogs as catalogs_db
from app.db import jobs as jobs_db
from app.models.catalog import CatalogSummary, ScientificCatalog
from app.routers._deps import require_user

router = APIRouter(prefix="/catalogs", tags=["catalogs"])


@router.get("", response_model=list[CatalogSummary])
async def list_catalogs(user_id: int = Depends(require_user)) -> list[CatalogSummary]:
    return catalogs_db.list_catalogs(user_id)


@router.get("/{catalog_id}", response_model=ScientificCatalog)
async def get_catalog(
    catalog_id: int,
    user_id: int = Depends(require_user),
) -> ScientificCatalog:
    cat = catalogs_db.get_catalog(catalog_id, user_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Catalog not found")
    return cat


@router.delete("/{catalog_id}")
async def delete_catalog(
    catalog_id: int,
    user_id: int = Depends(require_user),
) -> dict:
    if not catalogs_db.delete_catalog(catalog_id, user_id):
        raise HTTPException(status_code=404, detail="Catalog not found")
    jobs_db.nullify_catalog(catalog_id)
    return {"status": "ok"}
