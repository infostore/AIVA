"""
인증 스키마
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """로그인 요청 스키마"""
    username: str
    password: str


class RegisterRequest(BaseModel):
    """회원가입 요청 스키마"""
    email: EmailStr
    username: str
    password: str = Field(..., min_length=8)
    password_confirm: str
    full_name: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """리프레시 토큰 요청 스키마"""
    refresh_token: str


class VerifyTokenRequest(BaseModel):
    """토큰 검증 요청 스키마"""
    token: str


class PasswordResetRequest(BaseModel):
    """비밀번호 재설정 요청 스키마"""
    email: EmailStr


class PasswordResetConfirmRequest(BaseModel):
    """비밀번호 재설정 확인 요청 스키마"""
    token: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str


class EmailVerificationRequest(BaseModel):
    """이메일 인증 요청 스키마"""
    token: str


class TwoFactorLoginRequest(BaseModel):
    """2단계 인증 로그인 요청 스키마"""
    token: str  # 임시 액세스 토큰
    code: str = Field(..., min_length=6, max_length=6) 