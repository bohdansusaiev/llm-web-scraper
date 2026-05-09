"""Generic LLM-driven scraping endpoint. The diploma's core engine, exposed."""
from fastapi import APIRouter, Depends

from app.models.extraction import GenericExtractRequest, GenericExtractResponse
from app.routers._deps import require_user
from app.services.generic_extract import run_generic_extract

router = APIRouter(prefix="/scrape", tags=["scrape"])


@router.post("", response_model=GenericExtractResponse)
async def scrape(
    req: GenericExtractRequest,
    user_id: int = Depends(require_user),
) -> GenericExtractResponse:
    return await run_generic_extract(req)
