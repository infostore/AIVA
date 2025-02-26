"""
애플리케이션 설정
"""
import os
from datetime import timedelta
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    """
    # 기본 설정
    PROJECT_NAME: str = "Auth Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    
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
    
    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "auth_service"
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # 이메일 설정
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = 587
    SMTP_HOST: Optional[str] = "smtp.gmail.com"
    SMTP_USER: Optional[str] = ""
    SMTP_PASSWORD: Optional[str] = ""
    EMAILS_FROM_EMAIL: Optional[EmailStr] = "info@example.com"
    EMAILS_FROM_NAME: Optional[str] = "Auth Service"
    
    # 2FA 설정
    TOTP_ISSUER: str = "New Data Collector"
    
    # 계산된 속성
    @property
    def access_token_expires(self) -> timedelta:
        """액세스 토큰 만료 시간"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    @property
    def refresh_token_expires(self) -> timedelta:
        """리프레시 토큰 만료 시간"""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )


# 설정 인스턴스 생성
settings = Settings()

# 데이터베이스 URI 설정
if settings.DATABASE_URI is None:
    settings.DATABASE_URI = PostgresDsn.build(
        scheme="postgresql",
        username=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        host=settings.POSTGRES_SERVER,
        port=int(settings.POSTGRES_PORT),
        path=f"/{settings.POSTGRES_DB or ''}",
    ) 