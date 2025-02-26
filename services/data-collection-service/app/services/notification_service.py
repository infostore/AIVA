"""
알림 서비스 연동 모듈
"""
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class NotificationService:
    """
    알림 서비스 클라이언트
    """
    
    def __init__(self):
        """
        클라이언트 초기화
        """
        self.base_url = "http://notification-service:8004/api/v1"  # 환경 변수로 이동 필요
        self.timeout = 10.0  # 요청 타임아웃 (초)
    
    async def send_task_completion_notification(
        self, task_id: int, task_type: str, status: str, result_summary: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        작업 완료 알림 전송
        
        Args:
            task_id: 작업 ID
            task_type: 작업 유형
            status: 작업 상태
            result_summary: 결과 요약 (선택 사항)
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = "/notifications"
        payload = {
            "type": "task_completion",
            "title": f"데이터 수집 작업 {status}",
            "message": f"작업 ID: {task_id}, 유형: {task_type}, 상태: {status}",
            "data": {
                "task_id": task_id,
                "task_type": task_type,
                "status": status
            }
        }
        
        if result_summary:
            payload["message"] += f"\n{result_summary}"
            payload["data"]["result_summary"] = result_summary
        
        return await self._post(endpoint, payload)
    
    async def send_error_notification(
        self, error_type: str, error_message: str, source: str
    ) -> Dict[str, Any]:
        """
        오류 알림 전송
        
        Args:
            error_type: 오류 유형
            error_message: 오류 메시지
            source: 오류 발생 위치
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = "/notifications"
        payload = {
            "type": "error",
            "title": f"데이터 수집 서비스 오류: {error_type}",
            "message": f"오류 메시지: {error_message}\n발생 위치: {source}",
            "data": {
                "error_type": error_type,
                "error_message": error_message,
                "source": source
            },
            "priority": "high"
        }
        
        return await self._post(endpoint, payload)
    
    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST 요청 전송
        
        Args:
            endpoint: API 엔드포인트
            data: 요청 데이터
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HTTPException: API 요청 실패 시
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"알림 서비스 오류 응답: {e.response.status_code} - {e.response.text}")
            # 알림 실패는 애플리케이션 실행에 영향을 주지 않도록 예외를 기록만 함
            return {"status": "error", "message": str(e)}
            
        except httpx.RequestError as e:
            logger.error(f"알림 서비스 요청 실패: {str(e)}")
            return {"status": "error", "message": str(e)}


# 전역 인스턴스
notification_service = NotificationService() 