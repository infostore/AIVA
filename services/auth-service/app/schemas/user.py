"""
사용자 관련 스키마
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user import UserRole


class UserBase(BaseModel):
    """
    사용자 기본 스키마
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_2fa_enabled: Optional[bool] = False
    roles: List[UserRole] = [UserRole.USER]


class UserCreate(BaseModel):
    """
    사용자 생성 스키마
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8)
    
    @field_validator("username", mode="before")
    @classmethod
    def username_alphanumeric(cls, v):
        """사용자명은 영문자와 숫자만 포함해야 합니다."""
        if not v.isalnum():
            raise ValueError("사용자명은 영문자와 숫자만 포함해야 합니다")
        return v


class UserUpdate(UserBase):
    """
    사용자 업데이트 스키마
    """
    password: Optional[str] = Field(None, min_length=8)


class UserInDBBase(UserBase):
    """
    데이터베이스 사용자 기본 스키마
    """
    id: str
    
    class Config:
        orm_mode = True


class User(UserInDBBase):
    """
    사용자 응답 스키마
    """
    pass


class UserInDB(UserInDBBase):
    """
    데이터베이스 사용자 스키마
    """
    hashed_password: str
    totp_secret: Optional[str] = None


class UserLogin(BaseModel):
    """
    사용자 로그인 스키마
    """
    email: EmailStr
    password: str


class UserPasswordUpdate(BaseModel):
    """사용자 비밀번호 업데이트 스키마"""
    current_password: str
    new_password: str = Field(..., min_length=8)
    new_password_confirm: str
    
    @field_validator("new_password_confirm", mode="before")
    @classmethod
    def passwords_match(cls, v, values):
        """비밀번호 확인 검증"""
        if "new_password" in values and v != values["new_password"]:
            raise ValueError("새 비밀번호가 일치하지 않습니다")
        return v


class Token(BaseModel):
    """토큰 스키마"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """토큰 페이로드 스키마"""
    sub: str
    exp: int
    roles: List[UserRole]
    is_2fa_verified: bool = False


class RefreshTokenCreate(BaseModel):
    """리프레시 토큰 생성 스키마"""
    user_id: str
    token: str
    expires_at: datetime


class TwoFactorSetup(BaseModel):
    """2단계 인증 설정 스키마"""
    secret: str
    qr_code: str


class TwoFactorVerify(BaseModel):
    """2단계 인증 검증 스키마"""
    code: str = Field(..., min_length=6, max_length=6) 