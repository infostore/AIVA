"""
데이터 수집 작업 모델
"""
import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class CollectionType(str, enum.Enum):
    """수집 유형"""
    STOCK_PRICE = "stock_price"
    STOCK_INFO = "stock_info"
    TRADING_TREND = "trading_trend"
    QUARTERLY_REVENUE = "quarterly_revenue"
    MARKET_INDEX = "market_index"
    NEWS = "news"
    DISCLOSURE = "disclosure"


class TaskStatus(str, enum.Enum):
    """작업 상태"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CollectionTask(Base):
    """데이터 수집 작업 모델"""
    __tablename__ = "collection_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    collection_type = Column(Enum(CollectionType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    parameters = Column(Text, nullable=True)  # JSON 형식의 매개변수
    scheduled_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    max_retries = Column(Integer, default=3, nullable=False)
    is_recurring = Column(Boolean, default=False, nullable=False)
    interval_minutes = Column(Integer, nullable=True)  # 반복 주기 (분)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 관계 설정
    results = relationship("CollectionResult", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<CollectionTask(id={self.id}, type={self.collection_type}, status={self.status})>"


class CollectionResult(Base):
    """데이터 수집 결과 모델"""
    __tablename__ = "collection_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("collection_tasks.id"), nullable=False)
    data_count = Column(Integer, default=0, nullable=False)  # 수집된 데이터 수
    storage_location = Column(String(255), nullable=True)  # 저장 위치 (URL 또는 경로)
    metadata = Column(Text, nullable=True)  # JSON 형식의 메타데이터
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 관계 설정
    task = relationship("CollectionTask", back_populates="results")
    
    def __repr__(self):
        return f"<CollectionResult(id={self.id}, task_id={self.task_id}, data_count={self.data_count})>" 