from fastapi import APIRouter, HTTPException

from app.db import users as users_db
from app.models.auth import LoginRequest, RegisterRequest, UserPublic

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
async def register(req: RegisterRequest) -> dict:
    if not users_db.register_user(req.username, req.password):
        raise HTTPException(status_code=409, detail="Username already exists")
    return {"status": "ok"}


@router.post("/login", response_model=UserPublic)
async def login(req: LoginRequest) -> UserPublic:
    user = users_db.login_user(req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return UserPublic(id=user["id"], username=user["username"])
