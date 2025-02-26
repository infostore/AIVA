"""
API 라우터 설정
"""
from fastapi import APIRouter

from app.api.v1.endpoints import collection_tasks

api_router = APIRouter()

# 데이터 수집 작업 엔드포인트 등록
api_router.include_router(
    collection_tasks.router, prefix="/collection-tasks", tags=["collection-tasks"]
) 