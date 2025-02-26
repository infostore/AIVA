"""
API v1 라우트
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["인증"])
api_router.include_router(users.router, prefix="/users", tags=["사용자"]) 