"""
서비스 프록시 모듈
"""
import logging
from typing import Any, Dict, List, Optional, Union

import httpx
from fastapi import HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse

from app.config import settings

logger = logging.getLogger(__name__)


class ServiceProxy:
    """마이크로서비스 프록시"""

    def __init__(self, timeout: float = 30.0):
        """
        서비스 프록시 초기화
        
        Args:
            timeout: 요청 타임아웃 (초)
        """
        self.timeout = timeout
        self.service_urls = {
            "auth": settings.AUTH_SERVICE_URL,
            "collectors": settings.DATA_COLLECTION_SERVICE_URL,
            "stocks": settings.DATA_STORAGE_SERVICE_URL,
            "analysis": settings.ANALYSIS_SERVICE_URL,
            "notifications": settings.NOTIFICATION_SERVICE_URL,
        }
    
    async def forward_request(
        self, request: Request, service_name: str, path: str
    ) -> Response:
        """
        요청을 마이크로서비스로 전달
        
        Args:
            request: 원본 요청
            service_name: 대상 서비스 이름
            path: 대상 경로
            
        Returns:
            Response: 마이크로서비스 응답
            
        Raises:
            HTTPException: 요청 처리 중 오류 발생 시
        """
        # 서비스 URL 확인
        service_url = self.service_urls.get(service_name)
        if not service_url:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"서비스 '{service_name}'을(를) 찾을 수 없습니다.",
            )
        
        # 대상 URL 구성
        target_url = f"{service_url}{path}"
        
        # 요청 헤더 복사 (일부 헤더 제외)
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # 요청 본문 읽기
        body = await request.body()
        
        try:
            # 비동기 HTTP 클라이언트로 요청 전달
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=request.method,
                    url=target_url,
                    headers=headers,
                    content=body,
                    params=request.query_params,
                    follow_redirects=True,
                )
                
                # 응답 반환
                return await self._create_response(response)
        except httpx.TimeoutException:
            logger.error("요청 타임아웃: %s %s", request.method, target_url)
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="서비스 요청 시간이 초과되었습니다.",
            )
        except httpx.RequestError as e:
            logger.error("요청 오류: %s %s - %s", request.method, target_url, str(e))
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="서비스 요청 중 오류가 발생했습니다.",
            )
        except Exception as e:
            logger.error("예상치 못한 오류: %s %s - %s", request.method, target_url, str(e))
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="요청을 처리하는 중 오류가 발생했습니다.",
            )
    
    async def _create_response(self, response: httpx.Response) -> Response:
        """
        마이크로서비스 응답을 FastAPI 응답으로 변환
        
        Args:
            response: HTTPX 응답
            
        Returns:
            Response: FastAPI 응답
        """
        # 스트리밍 응답인 경우
        if "transfer-encoding" in response.headers and response.headers["transfer-encoding"].lower() == "chunked":
            return StreamingResponse(
                content=response.aiter_bytes(),
                status_code=response.status_code,
                headers=dict(response.headers),
            )
        
        # 일반 응답
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type"),
        ) 