"""
토큰 관련 스키마
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class Token(BaseModel):
    """
    토큰 응답 스키마
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    requires_2fa: bool = False


class TokenPayload(BaseModel):
    """
    토큰 페이로드 스키마
    """
    sub: str
    exp: int
    roles: List[str] = []
    is_2fa_verified: bool = False


class RefreshToken(BaseModel):
    """
    리프레시 토큰 요청 스키마
    """
    refresh_token: str


class TOTPVerify(BaseModel):
    """
    TOTP 인증 요청 스키마
    """
    code: str = Field(..., min_length=6, max_length=6)


class TOTPSetupResponse(BaseModel):
    """
    TOTP 설정 응답 스키마
    """
    secret: str
    qrcode: str
    uri: Optional[str] = None 