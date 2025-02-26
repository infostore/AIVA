"""
API 버전 1 라우터
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import (
    fundamental,
    health,
    prediction,
    technical,
    text_analysis,
)

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(technical.router, prefix="/technical", tags=["technical"])
api_router.include_router(fundamental.router, prefix="/fundamental", tags=["fundamental"])
api_router.include_router(prediction.router, prefix="/prediction", tags=["prediction"])
api_router.include_router(text_analysis.router, prefix="/text", tags=["text_analysis"]) 