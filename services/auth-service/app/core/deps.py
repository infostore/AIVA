"""
의존성 주입 유틸리티
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.core.security import create_access_token
from app.crud.user import user_crud
from app.db.session import SessionLocal
from app.models.user import UserRole
from app.schemas.token import TokenPayload

# OAuth2 인증 스키마
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)


def get_db() -> Generator[Session, None, None]:
    """
    데이터베이스 세션 의존성
    
    Yields:
        Session: 데이터베이스 세션
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> Optional[dict]:
    """
    현재 인증된 사용자 정보 가져오기
    
    Args:
        db: 데이터베이스 세션
        token: JWT 토큰
        
    Returns:
        dict: 사용자 정보
        
    Raises:
        HTTPException: 인증 실패 시
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 정보",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = user_crud.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    
    return user


def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    현재 활성화된 사용자 정보 가져오기
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        dict: 활성화된 사용자 정보
        
    Raises:
        HTTPException: 사용자가 비활성화된 경우
    """
    if current_user.is_active is not True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다",
        )
    
    return current_user


def get_current_verified_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """
    2단계 인증이 완료된 사용자 정보 가져오기
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        dict: 2단계 인증이 완료된 사용자 정보
        
    Raises:
        HTTPException: 2단계 인증이 완료되지 않은 경우
    """
    if not current_user.get("is_2fa_verified", False):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2단계 인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


def check_admin_permission(
    current_user: dict = Depends(get_current_active_user),
) -> dict:
    """
    관리자 권한 확인
    
    Args:
        current_user: 현재 활성화된 사용자
        
    Returns:
        dict: 관리자 권한이 있는 사용자 정보
        
    Raises:
        HTTPException: 관리자 권한이 없는 경우
    """
    if UserRole.ADMIN not in current_user.roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다",
        )
    
    return current_user 