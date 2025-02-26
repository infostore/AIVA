"""
속도 제한 미들웨어
"""
import time
from typing import Dict, List, Optional, Tuple

import redis
from fastapi import HTTPException, Request, Response, status

from app.config import settings


class RateLimitMiddleware:
    """요청 속도 제한 미들웨어"""

    def __init__(
        self,
        redis_host: str = settings.REDIS_HOST,
        redis_port: int = settings.REDIS_PORT,
        redis_db: int = settings.REDIS_DB,
        redis_password: Optional[str] = settings.REDIS_PASSWORD,
        rate_limit_enabled: bool = settings.RATE_LIMIT_ENABLED,
        default_rate_limit: int = settings.RATE_LIMIT_DEFAULT,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        속도 제한 미들웨어 초기화
        
        Args:
            redis_host: Redis 호스트
            redis_port: Redis 포트
            redis_db: Redis DB 번호
            redis_password: Redis 비밀번호
            rate_limit_enabled: 속도 제한 활성화 여부
            default_rate_limit: 기본 속도 제한 (분당 요청 수)
            exclude_paths: 속도 제한에서 제외할 경로 목록
        """
        self.rate_limit_enabled = rate_limit_enabled
        self.default_rate_limit = default_rate_limit
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        
        # Redis 클라이언트 초기화
        self.redis = None
        if self.rate_limit_enabled:
            self.redis = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                password=redis_password,
                decode_responses=True,
            )
    
    async def __call__(self, request: Request, call_next):
        """
        요청에 대한 속도 제한 적용
        
        Args:
            request: HTTP 요청
            call_next: 다음 미들웨어 호출 함수
            
        Returns:
            Response: HTTP 응답
            
        Raises:
            HTTPException: 속도 제한 초과 시 발생
        """
        # 속도 제한이 비활성화되어 있거나 제외 경로인 경우 바로 다음 미들웨어 호출
        if not self.rate_limit_enabled or self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Redis 클라이언트가 없는 경우 다음 미들웨어 호출
        if self.redis is None:
            return await call_next(request)
        
        # 클라이언트 식별자 (IP 주소 또는 사용자 ID)
        client_id = self._get_client_id(request)
        
        # 속도 제한 확인
        current_count, time_window = self._check_rate_limit(client_id)
        
        # 속도 제한 초과 시 429 오류 반환
        if current_count > self.default_rate_limit:
            reset_time = int(time_window - time.time())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"속도 제한을 초과했습니다. {reset_time}초 후에 다시 시도하세요.",
                headers={
                    "X-RateLimit-Limit": str(self.default_rate_limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_time),
                },
            )
        
        # 응답 생성
        response = await call_next(request)
        
        # 응답 헤더에 속도 제한 정보 추가
        if isinstance(response, Response):
            remaining = max(0, self.default_rate_limit - current_count)
            reset_time = int(time_window - time.time())
            response.headers["X-RateLimit-Limit"] = str(self.default_rate_limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_time)
        
        return response
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        속도 제한에서 제외할 경로인지 확인
        
        Args:
            path: 요청 경로
            
        Returns:
            bool: 제외 경로이면 True
        """
        for exclude_path in self.exclude_paths:
            if path.startswith(exclude_path):
                return True
        return False
    
    def _get_client_id(self, request: Request) -> str:
        """
        클라이언트 식별자 반환
        
        Args:
            request: HTTP 요청
            
        Returns:
            str: 클라이언트 식별자
        """
        # 인증된 사용자인 경우 사용자 ID 사용
        if hasattr(request.state, "user") and request.state.user:
            return f"user:{request.state.user.get('sub', '')}"
        
        # 인증되지 않은 경우 IP 주소 사용
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return f"ip:{forwarded_for.split(',')[0].strip()}"
        
        return f"ip:{request.client.host if request.client else 'unknown'}"
    
    def _check_rate_limit(self, client_id: str) -> Tuple[int, float]:
        """
        속도 제한 확인 및 요청 카운트 증가
        
        Args:
            client_id: 클라이언트 식별자
            
        Returns:
            Tuple[int, float]: (현재 요청 수, 시간 윈도우 종료 시간)
        """
        # 현재 시간 (초)
        current_time = time.time()
        
        # 시간 윈도우 (1분)
        time_window = current_time + 60
        
        # Redis 키
        key = f"rate_limit:{client_id}:{int(current_time / 60)}"
        
        # 파이프라인으로 여러 명령 실행
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, 60)
        result = pipe.execute()
        
        # 현재 요청 수
        current_count = result[0]
        
        return current_count, time_window 