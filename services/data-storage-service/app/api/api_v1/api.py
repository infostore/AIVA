"""
API 버전 1 라우터
"""
from fastapi import APIRouter

from app.api.api_v1.endpoints import stocks, prices, financials, health

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(stocks.router, prefix="/stocks", tags=["stocks"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(financials.router, prefix="/financials", tags=["financials"]) 