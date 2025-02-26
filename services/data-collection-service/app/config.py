"""
설정 모듈
"""
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, Field, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스
    """
    # 기본 설정
    PROJECT_NAME: str = "Data Collection Service"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # 보안 설정
    SECRET_KEY: str = "your-secret-key-here"
    
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
    POSTGRES_DB: str = "data_collection_service"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: Optional[PostgresDsn] = None
    
    # 데이터 수집 설정
    COLLECTION_INTERVAL_MINUTES: int = 60  # 기본 수집 주기 (분)
    MAX_CONCURRENT_COLLECTIONS: int = 5  # 최대 동시 수집 작업 수
    
    # 외부 API 설정
    STOCK_API_BASE_URL: str = "https://api.example.com/stocks"
    STOCK_API_KEY: str = "your-api-key-here"
    
    # 메시지 큐 설정
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"
    
    # 데이터 스토리지 서비스 설정
    DATA_STORAGE_SERVICE_URL: str = "http://data-storage-service:8003/api/v1"
    
    # 모델 설정
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    @property
    def get_database_uri(self) -> PostgresDsn:
        """데이터베이스 URI 생성"""
        if self.DATABASE_URI:
            return self.DATABASE_URI
        
        return PostgresDsn.build(
            scheme="postgresql",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=f"/{self.POSTGRES_DB}",
        )


settings = Settings() 