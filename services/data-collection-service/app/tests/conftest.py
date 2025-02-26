"""
테스트 설정 모듈
"""
import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app.api.deps import get_db
from app.db.session import Base
from app.main import app

# 테스트용 데이터베이스 URL
TEST_DATABASE_URL = "sqlite:///./test.db"
TEST_ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


# 동기 엔진 및 세션
engine = create_engine(
    TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 비동기 엔진 및 세션
async_engine = create_async_engine(
    TEST_ASYNC_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=NullPool,
)
AsyncTestingSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """
    pytest-asyncio 이벤트 루프 설정
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator:
    """
    테스트용 비동기 데이터베이스 세션 제공
    """
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncTestingSessionLocal() as session:
        yield session
    
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(db):
    """
    의존성 오버라이드 함수
    """
    async def _override_get_db():
        try:
            yield db
        finally:
            pass
    
    return _override_get_db


@pytest.fixture(scope="function")
def test_app(override_get_db) -> Generator[FastAPI, None, None]:
    """
    테스트용 FastAPI 애플리케이션 제공
    """
    app.dependency_overrides[get_db] = override_get_db
    yield app
    app.dependency_overrides = {}


@pytest.fixture(scope="function")
def client(test_app) -> Generator[TestClient, None, None]:
    """
    테스트 클라이언트 제공
    """
    with TestClient(test_app) as c:
        yield c 