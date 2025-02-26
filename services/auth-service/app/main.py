"""
메인 애플리케이션
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1 import api_router
from app.config import settings
from app.db.init_db import init_db
from app.db.session import SessionLocal

# 로거 설정
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 시작 및 종료 시 실행되는 이벤트 핸들러
    """
    # 애플리케이션 시작 시 실행
    logger.info("%s 시작", settings.PROJECT_NAME)
    
    # 데이터베이스 초기화
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error("데이터베이스 초기화 중 오류 발생: %s", str(e))
    finally:
        db.close()
    
    yield
    
    # 애플리케이션 종료 시 실행
    logger.info("%s 종료", settings.PROJECT_NAME)


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="인증 서비스 API",
    version="0.1.0",
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


@app.get("/health")
def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "ok"} 