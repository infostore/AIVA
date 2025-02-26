"""
데이터베이스 세션 관리
"""
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

# 데이터베이스 엔진 생성
engine = create_engine(
    str(settings.get_database_uri),
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 기본 모델 클래스
Base = declarative_base()


def get_db() -> Generator:
    """
    데이터베이스 세션 의존성
    
    Yields:
        Session: 데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 