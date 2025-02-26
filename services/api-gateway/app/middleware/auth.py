"""
인증 미들웨어
"""
import logging
from typing import Dict, List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config import settings

logger = logging.getLogger(__name__)
security = HTTPBearer()


class AuthMiddleware:
    """JWT 토큰 검증 미들웨어"""

    def __init__(
        self,
        public_paths: Optional[List[str]] = None,
        exclude_paths: Optional[List[str]] = None,
    ):
        """
        인증 미들웨어 초기화
        
        Args:
            public_paths: 인증이 필요 없는 경로 목록
            exclude_paths: 인증 검사에서 제외할 경로 목록
        """
        self.public_paths = public_paths or [
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
            "/health",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.exclude_paths = exclude_paths or []

    async def __call__(self, request: Request) -> None:
        """
        요청에 대한 인증 검증
        
        Args:
            request: HTTP 요청
            
        Raises:
            HTTPException: 인증 실패 시 발생
        """
        # 인증이 필요 없는 경로인지 확인
        if self._is_public_path(request.url.path):
            return
        
        # 인증 헤더 추출
        try:
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="인증 헤더가 없습니다.",
                )
            
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Bearer 인증이 필요합니다.",
                )
            
            # 토큰 검증
            payload = self._verify_token(token)
            
            # 요청 상태에 사용자 정보 추가
            request.state.user = payload
            
        except HTTPException as e:
            raise e
        except Exception as e:
            logger.error("인증 오류: %s", str(e))
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="인증에 실패했습니다.",
            )
    
    def _is_public_path(self, path: str) -> bool:
        """
        인증이 필요 없는 경로인지 확인
        
        Args:
            path: 요청 경로
            
        Returns:
            bool: 인증이 필요 없는 경로이면 True
        """
        # 제외 경로 확인
        if path in self.exclude_paths:
            return True
        
        # 공개 경로 확인
        for public_path in self.public_paths:
            if path.startswith(public_path):
                return True
        
        return False
    
    def _verify_token(self, token: str) -> Dict:
        """
        JWT 토큰 검증
        
        Args:
            token: JWT 토큰
            
        Returns:
            Dict: 토큰 페이로드
            
        Raises:
            HTTPException: 토큰 검증 실패 시 발생
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 토큰입니다.",
            )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """
    현재 인증된 사용자 정보 반환
    
    Args:
        credentials: HTTP 인증 정보
        
    Returns:
        Dict: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시 발생
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
        ) 