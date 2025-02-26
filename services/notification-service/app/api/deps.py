"""
API 의존성 모듈
"""
from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.session import get_db

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False
)


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[dict]:
    """
    현재 사용자 정보 가져오기
    
    Args:
        db: 데이터베이스 세션
        token: JWT 토큰
        
    Returns:
        Optional[dict]: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시
    """
    if not token:
        return None
    
    try:
        # 토큰 디코딩
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=["HS256"]
        )
        
        # 사용자 ID 추출
        user_id = payload.get("sub")
        if not user_id:
            return None
        
        # 사용자 정보 반환
        return {"id": user_id, "role": payload.get("role", "user")}
        
    except (JWTError, ValidationError):
        return None


async def get_current_active_user(
    current_user: Optional[dict] = Depends(get_current_user),
) -> dict:
    """
    현재 활성 사용자 정보 가져오기
    
    Args:
        current_user: 현재 사용자 정보
        
    Returns:
        dict: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user 