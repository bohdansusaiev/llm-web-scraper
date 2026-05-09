"""Research jobs — POST /research starts an async job; GET /research/{id} polls it."""
import asyncio
from fastapi import APIRouter, Depends, HTTPException

from app.db import jobs as jobs_db
from app.models.catalog import ResearchRequest
from app.models.jobs import ResearchJob, ResearchJobCreate
from app.routers._deps import require_user
from app.services.pipeline import run_research_job

router = APIRouter(prefix="/research", tags=["research"])


@router.post("", response_model=ResearchJobCreate, status_code=202)
async def start_research(
    req: ResearchRequest,
    user_id: int = Depends(require_user),
) -> ResearchJobCreate:
    job_id = jobs_db.create_job(user_id, req.topic, req.language)
    asyncio.create_task(run_research_job(job_id, user_id, req))
    return ResearchJobCreate(job_id=job_id)


@router.get("/{job_id}", response_model=ResearchJob)
async def get_research_job(
    job_id: int,
    user_id: int = Depends(require_user),
) -> ResearchJob:
    job = jobs_db.get_job(job_id, user_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("", response_model=list[ResearchJob])
async def list_research_jobs(
    limit: int = 20,
    user_id: int = Depends(require_user),
) -> list[ResearchJob]:
    return jobs_db.list_jobs(user_id, limit=limit)
