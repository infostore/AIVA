"""
설정 모듈
"""
import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    애플리케이션 설정
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    PROJECT_NAME: str = "Notification Service"
    DEBUG: bool = False
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """
        CORS 오리진 목록 검증
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # 데이터베이스 설정
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        """
        데이터베이스 URI 생성
        """
        if isinstance(v, str):
            return v
        
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT", 5432)),
            path=f"/{values.get('POSTGRES_DB', '')}",
        )
    
    # 이메일 설정
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: Optional[str] = ""
    SMTP_PASSWORD: Optional[str] = ""
    EMAIL_FROM: EmailStr
    EMAIL_FROM_NAME: str
    
    # RabbitMQ 설정
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int
    RABBITMQ_USER: str
    RABBITMQ_PASSWORD: str
    
    # Redis 설정
    REDIS_HOST: str
    REDIS_PORT: int
    
    # 알림 설정
    NOTIFICATION_RETENTION_DAYS: int = 30
    MAX_NOTIFICATIONS_PER_USER: int = 1000
    
    class Config:
        """
        설정 클래스 설정
        """
        case_sensitive = True
        env_file = ".env"


settings = Settings() 