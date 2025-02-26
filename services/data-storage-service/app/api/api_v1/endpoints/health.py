"""
건강 체크 엔드포인트
"""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

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
        "service": "data-storage-service"
    }


@router.get("/db")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    """
    데이터베이스 연결 상태 확인
    
    Args:
        db: 데이터베이스 세션
        
    Returns:
        dict: 데이터베이스 상태 정보
    """
    try:
        # 간단한 쿼리 실행
        await db.execute(text("SELECT 1"))
        return {
            "status": "ok",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "error": str(e)
        } 