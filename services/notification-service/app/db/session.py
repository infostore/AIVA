"""
데이터베이스 세션 모듈
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import settings

# 비동기 엔진 생성
engine = create_async_engine(str(settings.DATABASE_URI), echo=settings.DEBUG)

# 비동기 세션 생성
SessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

# 모델 기본 클래스
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션 의존성
    
    Yields:
        AsyncSession: 데이터베이스 세션
    """
    async with SessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise 