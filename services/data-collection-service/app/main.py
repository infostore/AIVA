"""
데이터 수집 서비스 메인 애플리케이션
"""
import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router
from app.config import settings
from app.db.init_db import init_db
from app.tasks.scheduler import scheduler

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI: 애플리케이션 인스턴스
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description="데이터 수집 서비스 API",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    
    # CORS 미들웨어 설정
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # API 라우터 등록
    application.include_router(api_router, prefix=settings.API_V1_STR)
    
    return application


app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러
    """
    logger.info("애플리케이션 시작")
    
    # 데이터베이스 초기화
    init_db()
    
    # 스케줄러 시작
    asyncio.create_task(scheduler.start())
    logger.info("작업 스케줄러 시작됨")


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러
    """
    logger.info("애플리케이션 종료")
    
    # 스케줄러 중지
    await scheduler.stop()
    logger.info("작업 스케줄러 중지됨")


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "ok"} 