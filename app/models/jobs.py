"""Async research job tracking — exposed via /research/{job_id}."""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    DISCOVERING = "discovering"
    FILTERING = "filtering"
    EXTRACTING = "extracting"
    TRANSLATING = "translating"
    SAVING = "saving"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchJob(BaseModel):
    id: int
    user_id: int
    topic: str
    language: str = "en"
    status: JobStatus = JobStatus.PENDING
    progress: int = Field(default=0, ge=0, le=100,
        description="0-100. Coarse-grained: discovery=20, filtering=30, extraction=20-90, save=100.")
    message: str = Field(default="", description="Human-readable current step description.")
    catalog_id: Optional[int] = None
    error: str = ""
    created_at: datetime
    updated_at: datetime


class ResearchJobCreate(BaseModel):
    """Returned immediately from POST /research."""
    job_id: int
