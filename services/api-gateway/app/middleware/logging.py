"""
로깅 미들웨어
"""
import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response

logger = logging.getLogger(__name__)


class LoggingMiddleware:
    """요청/응답 로깅 미들웨어"""

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        요청 및 응답 로깅
        
        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어 호출 함수
            
        Returns:
            Response: HTTP 응답
        """
        # 요청 ID 생성
        request_id = str(uuid.uuid4())
        
        # 요청 시작 시간
        start_time = time.time()
        
        # 요청 정보 로깅
        self._log_request(request, request_id)
        
        # 응답 생성
        try:
            response = await call_next(request)
            
            # 처리 시간 계산
            process_time = time.time() - start_time
            
            # 응답 정보 로깅
            self._log_response(request, response, request_id, process_time)
            
            # 응답 헤더에 요청 ID 추가
            response.headers["X-Request-ID"] = request_id
            
            return response
        except Exception as e:
            # 오류 로깅
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"(ID: {request_id}) - Error: {str(e)}"
            )
            raise
    
    def _log_request(self, request: Request, request_id: str) -> None:
        """
        요청 정보 로깅
        
        Args:
            request: HTTP 요청
            request_id: 요청 ID
        """
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("User-Agent", "unknown")
        
        logger.info(
            f"Request started: {request.method} {request.url.path} "
            f"(ID: {request_id}, Client: {client_host}, "
            f"User-Agent: {user_agent})"
        )
    
    def _log_response(
        self, request: Request, response: Response, request_id: str, process_time: float
    ) -> None:
        """
        응답 정보 로깅
        
        Args:
            request: HTTP 요청
            response: HTTP 응답
            request_id: 요청 ID
            process_time: 처리 시간 (초)
        """
        logger.info(
            f"Request completed: {request.method} {request.url.path} "
            f"(ID: {request_id}, Status: {response.status_code}, "
            f"Time: {process_time:.3f}s)"
        ) 