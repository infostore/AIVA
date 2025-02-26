"""
보안 관련 유틸리티
"""
import base64
import os
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import pyotp
import qrcode
from jose import jwt
from passlib.context import CryptContext

from app.config import settings
from app.models.user import UserRole

# 비밀번호 해싱 컨텍스트
pwd_context = CryptContext(schemes=[settings.PASSWORD_HASH_ALGORITHM], deprecated="auto")


def create_access_token(
    subject: Union[str, Any],
    roles: List[UserRole],
    expires_delta: Optional[timedelta] = None,
    is_2fa_verified: bool = False,
) -> str:
    """
    액세스 토큰 생성
    
    Args:
        subject: 토큰 주체 (일반적으로 사용자 ID)
        roles: 사용자 역할 목록
        expires_delta: 만료 시간 (기본값: settings.access_token_expires)
        is_2fa_verified: 2단계 인증 완료 여부
        
    Returns:
        str: JWT 토큰
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + settings.access_token_expires
    
    to_encode = {
        "sub": str(subject),
        "exp": expire,
        "roles": [role.value for role in roles],
        "is_2fa_verified": is_2fa_verified,
    }
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    
    return encoded_jwt


def create_refresh_token() -> str:
    """
    리프레시 토큰 생성
    
    Returns:
        str: 리프레시 토큰
    """
    return secrets.token_urlsafe(64)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 검증
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        bool: 비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)


def generate_totp_secret() -> str:
    """
    TOTP 비밀키 생성
    
    Returns:
        str: TOTP 비밀키
    """
    return pyotp.random_base32()


def generate_totp_qrcode(username: str, secret: str) -> str:
    """
    TOTP QR 코드 생성
    
    Args:
        username: 사용자 이름
        secret: TOTP 비밀키
        
    Returns:
        str: QR 코드 이미지 (base64 인코딩)
    """
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(username, issuer_name=settings.TOTP_ISSUER)
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 이미지를 base64로 인코딩
    import io
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def verify_totp(secret: str, code: str) -> bool:
    """
    TOTP 코드 검증
    
    Args:
        secret: TOTP 비밀키
        code: 사용자가 입력한 코드
        
    Returns:
        bool: 코드 유효성 여부
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code) 