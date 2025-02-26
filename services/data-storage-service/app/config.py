"""
애플리케이션 설정 모듈
"""
import secrets
from typing import Any, List, Optional, Union

from pydantic import AnyHttpUrl, EmailStr, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    """
    # 기본 설정
    PROJECT_NAME: str = "Data Storage Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
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
    
    # 데이터베이스 설정
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "data_storage_service"
    POSTGRES_PORT: str = "5432"
    DATABASE_URI: Optional[PostgresDsn] = None
    
    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str]) -> Any:
        """데이터베이스 URI 생성"""
        if isinstance(v, str):
            return v
        
        # Pydantic v2에서는 클래스 속성을 직접 사용
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=cls.model_fields["POSTGRES_USER"].default,
            password=cls.model_fields["POSTGRES_PASSWORD"].default,
            host=cls.model_fields["POSTGRES_SERVER"].default,
            port=int(cls.model_fields["POSTGRES_PORT"].default),
            path=f"/{cls.model_fields['POSTGRES_DB'].default}",
        )
    
    # 캐시 설정
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    CACHE_EXPIRATION_SECONDS: int = 3600  # 1시간
    
    # 데이터 보관 설정
    DATA_RETENTION_DAYS: int = 365  # 1년
    
    # 모델 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings() 