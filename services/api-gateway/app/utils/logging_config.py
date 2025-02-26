"""
로깅 설정 유틸리티
"""
import logging
import sys
from typing import Dict, List, Optional

from app.config import settings


def configure_logging() -> None:
    """
    애플리케이션 로깅 설정
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # 개발 환경이 아닌 경우 일부 로그 레벨 조정
    if settings.ENVIRONMENT != "development":
        logging.getLogger("fastapi").setLevel(logging.WARNING)
        logging.getLogger("starlette").setLevel(logging.WARNING) 