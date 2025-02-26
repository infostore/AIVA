"""
애플리케이션 설정 모듈
"""
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, field_validator, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    """
    # 기본 설정
    PROJECT_NAME: str = "Analysis Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 서버 설정
    HOST: str = "0.0.0.0"
    PORT: int = 8002
    
    # 보안 설정
    SECRET_KEY: str = secrets.token_urlsafe(32)
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """CORS 설정 검증"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 데이터 스토리지 서비스 설정
    DATA_STORAGE_SERVICE_URL: str = "http://localhost:8000"
    
    # 분석 설정
    ANALYSIS_WINDOW_DAYS: int = 30  # 기본 분석 기간(일)
    MOVING_AVERAGE_PERIODS: List[int] = [5, 10, 20, 50, 200]  # 이동평균선 기간
    RSI_PERIOD: int = 14  # RSI 계산 기간
    MACD_FAST_PERIOD: int = 12  # MACD 빠른 기간
    MACD_SLOW_PERIOD: int = 26  # MACD 느린 기간
    MACD_SIGNAL_PERIOD: int = 9  # MACD 시그널 기간
    BOLLINGER_PERIOD: int = 20  # 볼린저 밴드 기간
    BOLLINGER_STD_DEV: float = 2.0  # 볼린저 밴드 표준편차
    
    # 캐시 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_EXPIRATION_SECONDS: int = 3600  # 1시간
    
    # 모델 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # API 키 설정
    OPENAI_API_KEY: str = ""
    
    @validator("OPENAI_API_KEY", pre=True)
    @classmethod
    def validate_openai_api_key(cls, v: str) -> str:
        """
        OpenAI API 키 검증
        """
        if not v:
            raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다")
        return v
    
    # Llama 모델 설정
    LLAMA_MODEL_PATH: str = "models/llama-2-7b-chat-q4_0.gguf"
    
    @validator("LLAMA_MODEL_PATH", pre=True)
    @classmethod
    def validate_llama_model_path(cls, v: str) -> str:
        """
        Llama 모델 경로 검증
        """
        if not v:
            raise ValueError("LLAMA_MODEL_PATH 환경 변수가 설정되지 않았습니다")
        return v


settings = Settings() 