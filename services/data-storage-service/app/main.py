"""
데이터 스토리지 서비스 메인 애플리케이션
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncEngine

from app.api.api_v1.api import api_router
from app.config import settings
from app.db.base import Base
from app.db.session import engine


# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작 및 종료 시 실행할 코드
    
    Args:
        app: FastAPI 애플리케이션
    """
    # 시작 시 실행
    logger.info("애플리케이션 시작")
    
    # 데이터베이스 테이블 생성
    async with engine.begin() as conn:
        # 개발 환경에서만 테이블 생성 (프로덕션에서는 마이그레이션 도구 사용)
        if settings.DEBUG:
            logger.info("데이터베이스 테이블 생성")
            await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # 종료 시 실행
    logger.info("애플리케이션 종료")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# API 라우터 등록
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """
    루트 엔드포인트
    
    Returns:
        dict: 서비스 정보
    """
    return {
        "service": settings.PROJECT_NAME,
        "version": "0.1.0",
        "api_version": "v1",
    } 