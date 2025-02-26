"""
API 의존성 모듈
"""
from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud
from app.config import settings
from app.db.session import SessionLocal
from app.models.user import User, UserRole
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
) -> User:
    """
    현재 인증된 사용자 정보 가져오기
    
    Args:
        db: 데이터베이스 세션
        token: JWT 토큰
        
    Returns:
        User: 사용자 객체
        
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
    
    user = crud.user.get(db, id=token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    현재 활성화된 사용자 정보 가져오기
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        User: 활성화된 사용자 객체
        
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
    current_user: User = Depends(get_current_user),
) -> User:
    """
    2단계 인증이 완료된 사용자 정보 가져오기
    
    Args:
        current_user: 현재 인증된 사용자
        
    Returns:
        User: 2단계 인증이 완료된 사용자 객체
        
    Raises:
        HTTPException: 2단계 인증이 완료되지 않은 경우
    """
    token_data = getattr(current_user, "token_data", None)
    is_2fa_verified = token_data and getattr(token_data, "is_2fa_verified", False)
    
    if (current_user.is_2fa_enabled is True) and (is_2fa_verified is not True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2단계 인증이 필요합니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user


def check_admin_permission(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    관리자 권한 확인
    
    Args:
        current_user: 현재 활성화된 사용자
        
    Returns:
        User: 관리자 권한이 있는 사용자 객체
        
    Raises:
        HTTPException: 관리자 권한이 없는 경우
    """
    if (current_user.roles == UserRole.ADMIN) is not True:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="권한이 없습니다",
        )
    
    return current_user 