"""
데이터베이스 모델의 기본 클래스 정의
"""
from typing import Any

from sqlalchemy import Column, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr


class Base(DeclarativeBase):
    """
    모든 데이터베이스 모델의 기본 클래스
    """
    # 생성 시간
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    # 업데이트 시간
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # 테이블 이름을 클래스 이름의 소문자 형태로 자동 생성
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.lower() 