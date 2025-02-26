"""
데이터베이스 세션 관리 모듈
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config import settings

# 비동기 데이터베이스 엔진 생성
engine = create_async_engine(
    str(settings.DATABASE_URI),
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

# 비동기 세션 팩토리 생성
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    데이터베이스 세션을 제공하는 의존성 함수
    
    Returns:
        AsyncGenerator[AsyncSession, None]: 비동기 데이터베이스 세션
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close() 