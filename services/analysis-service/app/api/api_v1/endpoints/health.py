"""
건강 체크 엔드포인트
"""
import httpx
from fastapi import APIRouter, HTTPException

from app.config import settings

router = APIRouter()


@router.get("/")
async def health_check():
    """
    서비스 건강 상태 확인
    
    Returns:
        dict: 서비스 상태 정보
    """
    return {
        "status": "ok",
        "service": "analysis-service"
    }


@router.get("/data-storage")
async def data_storage_health_check():
    """
    데이터 스토리지 서비스 연결 상태 확인
    
    Returns:
        dict: 데이터 스토리지 서비스 상태 정보
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/health")
            if response.status_code == 200:
                return {
                    "status": "ok",
                    "data_storage_service": "connected",
                    "details": response.json()
                }
            else:
                return {
                    "status": "error",
                    "data_storage_service": "error",
                    "details": f"Status code: {response.status_code}"
                }
    except Exception as e:
        return {
            "status": "error",
            "data_storage_service": "disconnected",
            "error": str(e)
        } 