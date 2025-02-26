"""
API Gateway 메인 애플리케이션
"""
import logging

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette_exporter import PrometheusMiddleware, handle_metrics

from app.config import settings
from app.middleware.auth import AuthMiddleware
from app.middleware.logging import LoggingMiddleware
from app.middleware.rate_limit import RateLimitMiddleware
from app.routes import api
from app.utils.logging_config import configure_logging

# 로깅 설정
configure_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    애플리케이션 라이프스팬 이벤트 핸들러
    
    Args:
        app: FastAPI 애플리케이션
    """
    # 시작 시 실행
    logger.info("%s 시작", settings.APP_NAME)
    yield
    # 종료 시 실행
    logger.info("%s 종료", settings.APP_NAME)


def create_app() -> FastAPI:
    """
    FastAPI 애플리케이션 생성
    
    Returns:
        FastAPI: FastAPI 애플리케이션
    """
    # FastAPI 애플리케이션 생성
    app = FastAPI(
        title=settings.APP_NAME,
        description="New Data Collector API Gateway",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )
    
    # CORS 미들웨어 추가
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 프로메테우스 미들웨어 추가
    app.add_middleware(
        PrometheusMiddleware,
        app_name="api_gateway",
        group_paths=True,
        prefix="api_gateway",
    )
    
    # 로깅 미들웨어 추가
    app.middleware("http")(LoggingMiddleware())
    
    # 속도 제한 미들웨어 추가
    app.middleware("http")(RateLimitMiddleware())
    
    # 인증 미들웨어 추가
    app.middleware("http")(AuthMiddleware())
    
    # 메트릭스 엔드포인트 추가
    app.add_route("/metrics", handle_metrics)
    
    # API 라우터 추가
    app.include_router(api.router, prefix=settings.API_PREFIX)
    
    return app


app = create_app() 