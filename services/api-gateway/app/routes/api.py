"""
API 라우트 모듈
"""
import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.config import settings
from app.middleware.auth import get_current_user
from app.proxy.service_proxy import ServiceProxy

logger = logging.getLogger(__name__)
router = APIRouter()
service_proxy = ServiceProxy()


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    API Gateway 상태 확인
    
    Returns:
        Dict[str, str]: 상태 정보
    """
    return {"status": "ok", "service": settings.APP_NAME}


@router.api_route(
    "/{service_name}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def proxy_endpoint(
    request: Request, service_name: str, path: str
) -> Response:
    """
    모든 API 요청을 적절한 마이크로서비스로 프록시
    
    Args:
        request: HTTP 요청
        service_name: 대상 서비스 이름
        path: 대상 경로
        
    Returns:
        Response: 마이크로서비스 응답
        
    Raises:
        HTTPException: 요청 처리 중 오류 발생 시
    """
    # 서비스 이름 검증
    if service_name not in settings.SERVICE_PATH_MAPPING:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"서비스 '{service_name}'을(를) 찾을 수 없습니다.",
        )
    
    # 경로 구성
    full_path = f"/{path}"
    
    try:
        # 요청 전달
        return await service_proxy.forward_request(request, service_name, full_path)
    except HTTPException as e:
        # HTTP 예외는 그대로 전달
        raise e
    except Exception as e:
        # 기타 예외는 로깅 후 500 오류 반환
        logger.error("프록시 오류: %s", str(e))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "status": "error",
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "요청을 처리하는 중 오류가 발생했습니다.",
                },
            },
        ) 