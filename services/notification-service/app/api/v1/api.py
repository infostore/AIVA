"""
API v1 라우터 모듈
"""
from fastapi import APIRouter

from app.api.v1.endpoints import notifications

api_router = APIRouter()

# 엔드포인트 라우터 포함
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"]) 