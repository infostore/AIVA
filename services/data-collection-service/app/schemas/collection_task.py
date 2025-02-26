"""
데이터 수집 작업 스키마
"""
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.models.collection_task import CollectionType, TaskStatus


class CollectionTaskBase(BaseModel):
    """수집 작업 기본 스키마"""
    collection_type: CollectionType
    parameters: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: bool = False
    interval_minutes: Optional[int] = None
    max_retries: int = 3


class CollectionTaskCreate(CollectionTaskBase):
    """수집 작업 생성 스키마"""
    pass


class CollectionTaskUpdate(BaseModel):
    """수집 작업 업데이트 스키마"""
    status: Optional[TaskStatus] = None
    parameters: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    is_recurring: Optional[bool] = None
    interval_minutes: Optional[int] = None
    max_retries: Optional[int] = None
    retry_count: Optional[int] = None
    error_message: Optional[str] = None


class CollectionResultBase(BaseModel):
    """수집 결과 기본 스키마"""
    task_id: UUID
    data_count: int = 0
    storage_location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class CollectionResultCreate(CollectionResultBase):
    """수집 결과 생성 스키마"""
    pass


class CollectionResult(CollectionResultBase):
    """수집 결과 응답 스키마"""
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class CollectionTask(CollectionTaskBase):
    """수집 작업 응답 스키마"""
    id: UUID
    status: TaskStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int
    created_at: datetime
    updated_at: datetime
    results: List[CollectionResult] = []
    
    class Config:
        from_attributes = True
    
    @field_validator("parameters", mode="before")
    @classmethod
    def parse_parameters(cls, v):
        """JSON 문자열을 딕셔너리로 변환"""
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        return v


class CollectionTaskList(BaseModel):
    """수집 작업 목록 응답 스키마"""
    items: List[CollectionTask]
    total: int
    page: int
    size: int
    pages: int 