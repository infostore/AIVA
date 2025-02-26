"""
API Gateway 서비스 설정
"""
from typing import Dict, List, Optional

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """API Gateway 서비스 설정"""

    # 기본 설정
    APP_NAME: str = "API Gateway Service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    # 서비스 URL
    AUTH_SERVICE_URL: str = "http://auth-service:8001"
    DATA_COLLECTION_SERVICE_URL: str = "http://data-collection-service:8002"
    DATA_STORAGE_SERVICE_URL: str = "http://data-storage-service:8003"
    ANALYSIS_SERVICE_URL: str = "http://analysis-service:8004"
    NOTIFICATION_SERVICE_URL: str = "http://notification-service:8005"
    
    # 서비스 경로 매핑
    SERVICE_PATH_MAPPING: Dict[str, str] = {
        "auth": "AUTH_SERVICE_URL",
        "collectors": "DATA_COLLECTION_SERVICE_URL",
        "stocks": "DATA_STORAGE_SERVICE_URL",
        "analysis": "ANALYSIS_SERVICE_URL",
        "notifications": "NOTIFICATION_SERVICE_URL",
    }
    
    # Redis 설정
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    # 속도 제한 설정
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT: int = 100  # 분당 요청 수
    
    # JWT 설정
    JWT_SECRET_KEY: str = Field(default="secret_key_for_development_only")
    JWT_ALGORITHM: str = "HS256"
    
    # 모델 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings() 