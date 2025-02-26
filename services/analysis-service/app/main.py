"""
애플리케이션 메인 모듈
"""
import logging
import os
from typing import Any

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.api_v1.api import api_router
from app.config import settings

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 환경 변수 확인
def check_environment():
    """
    필요한 환경 변수를 확인하는 함수
    """
    required_vars = ["OPENAI_API_KEY", "LLAMA_MODEL_PATH"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
        logger.warning("일부 기능이 제한될 수 있습니다.")


# FastAPI 애플리케이션 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
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


@app.on_event("startup")
async def startup_event():
    """
    애플리케이션 시작 시 실행되는 이벤트 핸들러
    """
    logger.info("애플리케이션 시작 중...")
    check_environment()
    logger.info("애플리케이션이 성공적으로 시작되었습니다.")


@app.on_event("shutdown")
async def shutdown_event():
    """
    애플리케이션 종료 시 실행되는 이벤트 핸들러
    """
    logger.info("애플리케이션 종료 중...")
    logger.info("애플리케이션이 성공적으로 종료되었습니다.")


@app.get("/")
def root() -> Any:
    """
    루트 엔드포인트
    """
    return {
        "message": "분석 서비스 API에 오신 것을 환영합니다.",
        "docs_url": f"{settings.API_V1_STR}/docs",
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    ) 