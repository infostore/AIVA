"""
기본 데이터 수집기
"""
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from sqlalchemy.orm import Session

from app.models.collection_task import CollectionResult, CollectionTask, TaskStatus

logger = logging.getLogger(__name__)


class BaseCollector(ABC):
    """
    기본 데이터 수집기 추상 클래스
    모든 데이터 수집기는 이 클래스를 상속받아야 함
    """
    
    def __init__(self, db: Session, task: CollectionTask):
        """
        초기화
        
        Args:
            db: 데이터베이스 세션
            task: 수집 작업 객체
        """
        self.db = db
        self.task = task
        self.result = None
    
    async def execute(self) -> CollectionResult:
        """
        수집 작업 실행
        
        Returns:
            CollectionResult: 수집 결과
        """
        try:
            # 작업 시작 상태 업데이트
            self.task.status = TaskStatus.RUNNING
            self.task.started_at = datetime.utcnow()
            self.db.add(self.task)
            self.db.commit()
            
            # 데이터 수집 실행
            data = await self.collect()
            
            # 데이터 저장
            storage_location, metadata = await self.store(data)
            
            # 결과 생성
            self.result = CollectionResult(
                task_id=self.task.id,
                data_count=len(data) if isinstance(data, list) else 1,
                storage_location=storage_location,
                metadata=json.dumps(metadata) if metadata else None,
            )
            self.db.add(self.result)
            
            # 작업 완료 상태 업데이트
            self.task.status = TaskStatus.COMPLETED
            self.task.completed_at = datetime.utcnow()
            self.db.add(self.task)
            self.db.commit()
            
            logger.info(
                f"수집 작업 완료: id={self.task.id}, type={self.task.collection_type}, "
                f"data_count={self.result.data_count}"
            )
            
            return self.result
            
        except Exception as e:
            # 오류 발생 시 상태 업데이트
            self.task.status = TaskStatus.FAILED
            self.task.error_message = str(e)
            self.task.retry_count += 1
            self.db.add(self.task)
            self.db.commit()
            
            logger.error(
                f"수집 작업 실패: id={self.task.id}, type={self.task.collection_type}, "
                f"error={str(e)}"
            )
            
            # 재시도 가능한 경우 재시도 작업 예약
            if self.task.retry_count < self.task.max_retries:
                # 재시도 로직 구현 (별도 스케줄러에서 처리)
                pass
            
            raise
    
    @abstractmethod
    async def collect(self) -> Any:
        """
        데이터 수집 로직 구현
        
        Returns:
            Any: 수집된 데이터
        """
        pass
    
    @abstractmethod
    async def store(self, data: Any) -> tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        수집된 데이터 저장 로직 구현
        
        Args:
            data: 수집된 데이터
            
        Returns:
            tuple: (저장 위치, 메타데이터)
        """
        pass
    
    async def _make_request(
        self, url: str, method: str = "GET", **kwargs
    ) -> httpx.Response:
        """
        HTTP 요청 헬퍼 메서드
        
        Args:
            url: 요청 URL
            method: HTTP 메서드
            **kwargs: 추가 매개변수
            
        Returns:
            httpx.Response: HTTP 응답
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(method, url, **kwargs)
            response.raise_for_status()
            return response
    
    def _parse_parameters(self) -> Dict[str, Any]:
        """
        작업 매개변수 파싱
        
        Returns:
            Dict[str, Any]: 파싱된 매개변수
        """
        if not self.task.parameters:
            return {}
        
        try:
            if isinstance(self.task.parameters, dict):
                return self.task.parameters
            return json.loads(self.task.parameters)
        except json.JSONDecodeError:
            logger.warning(f"매개변수 파싱 실패: {self.task.parameters}")
            return {} 