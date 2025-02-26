"""
알림 서비스 메인 애플리케이션
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.api import api_router
from app.config import settings
from app.db.init_db import init_db


# 로깅 설정
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작 및 종료 시 실행되는 이벤트 핸들러
    
    Args:
        app: FastAPI 애플리케이션 인스턴스
    """
    # 애플리케이션 시작 시 실행
    logger.info("애플리케이션 시작 중...")
    
    # 데이터베이스 초기화
    await init_db()
    
    logger.info("애플리케이션 시작 완료")
    
    yield
    
    # 애플리케이션 종료 시 실행
    logger.info("애플리케이션 종료 중...")
    logger.info("애플리케이션 종료 완료")


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI: 애플리케이션 인스턴스
    """
    # FastAPI 애플리케이션 생성
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="알림 서비스 API",
        version="0.1.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
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
    
    # 헬스 체크 엔드포인트
    @app.get("/health")
    async def health_check():
        """
        서비스 상태 확인 엔드포인트
        """
        return {"status": "ok", "service": settings.PROJECT_NAME}
    
    return app


# 애플리케이션 인스턴스 생성
app = create_app() 