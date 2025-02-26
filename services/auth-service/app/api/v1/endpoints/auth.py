"""
인증 관련 API 엔드포인트
"""
from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.security import (
    create_access_token,
    create_refresh_token,
    generate_totp_qrcode,
    generate_totp_secret,
    verify_totp,
)
from app.models.user import RefreshToken, User

router = APIRouter()


@router.post("/login", response_model=schemas.token.Token)
def login(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 호환 토큰 로그인, 액세스 토큰과 리프레시 토큰 발급
    """
    user = crud.user.authenticate(db, email=form_data.username, password=form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비활성화된 사용자입니다",
        )
    
    # 2단계 인증이 활성화된 경우
    requires_2fa = user.is_2fa_enabled
    
    # 액세스 토큰 생성
    access_token = create_access_token(
        subject=str(user.id),
        roles=[user.roles],
        is_2fa_verified=not requires_2fa,
    )
    
    # 리프레시 토큰 생성
    refresh_token_value = create_refresh_token()
    
    # 리프레시 토큰 저장
    refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_value,
        expires_at=datetime.utcnow() + timedelta(days=7),
    )
    db.add(refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
        "requires_2fa": requires_2fa,
    }


@router.post("/refresh", response_model=schemas.token.Token)
def refresh_token(
    token_data: schemas.token.RefreshToken,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    리프레시 토큰을 사용하여 새 액세스 토큰 발급
    """
    # 리프레시 토큰 조회
    refresh_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token_data.refresh_token)
        .filter(RefreshToken.expires_at > datetime.utcnow())
        .first()
    )
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않거나 만료된 리프레시 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 조회
    user = crud.user.get(db, id=refresh_token.user_id)
    if not user or not crud.user.is_active(user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 새 액세스 토큰 생성
    access_token = create_access_token(
        subject=str(user.id),
        roles=[user.roles],
        is_2fa_verified=not user.is_2fa_enabled,
    )
    
    # 새 리프레시 토큰 생성
    new_refresh_token = create_refresh_token()
    
    # 기존 리프레시 토큰 업데이트
    refresh_token.token = new_refresh_token
    refresh_token.expires_at = datetime.utcnow() + timedelta(days=7)
    db.add(refresh_token)
    db.commit()
    
    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
        "requires_2fa": user.is_2fa_enabled,
    }


@router.post("/register", response_model=schemas.user.User)
def register(
    user_in: schemas.auth.RegisterRequest,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    새 사용자 등록
    """
    # 이메일 중복 확인
    user = crud.user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 등록된 이메일입니다",
        )
    
    # 사용자명 중복 확인
    user = crud.user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 사용자명입니다",
        )
    
    # 비밀번호 확인
    if user_in.password != user_in.password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="비밀번호가 일치하지 않습니다",
        )
    
    # 사용자 생성
    user_create = schemas.user.UserCreate(
        email=user_in.email,
        username=user_in.username,
        password=user_in.password,
    )
    user = crud.user.create(db, obj_in=user_create)
    
    return user


@router.post("/2fa/setup", response_model=schemas.token.TOTPSetupResponse)
def setup_2fa(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    2단계 인증 설정
    """
    if current_user.is_2fa_enabled is True:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 2단계 인증이 활성화되어 있습니다",
        )
    
    # TOTP 비밀키 생성
    totp_secret = generate_totp_secret()
    
    # QR 코드 생성
    qrcode = generate_totp_qrcode(current_user.username, totp_secret)
    
    # 비밀키 저장 (아직 활성화하지 않음)
    current_user.totp_secret = totp_secret
    db.add(current_user)
    db.commit()
    
    return {
        "secret": totp_secret,
        "qrcode": qrcode,
    }


@router.post("/2fa/verify")
def verify_2fa(
    code_data: schemas.token.TOTPVerify,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    2단계 인증 활성화 및 검증
    """
    if not current_user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="2단계 인증이 설정되지 않았습니다",
        )
    
    # TOTP 코드 검증
    if not verify_totp(current_user.totp_secret, code_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 인증 코드입니다",
        )
    
    # 2단계 인증 활성화
    current_user.is_2fa_enabled = True
    db.add(current_user)
    db.commit()
    
    return {"message": "2단계 인증이 활성화되었습니다"}


@router.post("/2fa/login", response_model=schemas.token.Token)
def login_2fa(
    code_data: schemas.token.TOTPVerify,
    token_data: schemas.token.Token,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    2단계 인증 로그인
    """
    # 토큰에서 사용자 ID 추출
    from jose import jwt
    
    try:
        payload = jwt.decode(
            token_data.access_token,
            deps.settings.JWT_SECRET_KEY,
            algorithms=[deps.settings.JWT_ALGORITHM],
        )
        user_id = payload.get("sub")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 조회
    user = crud.user.get(db, id=user_id)
    if not user or not user.is_2fa_enabled or not user.totp_secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 사용자입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TOTP 코드 검증
    if not verify_totp(user.totp_secret, code_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="유효하지 않은 인증 코드입니다",
        )
    
    # 새 액세스 토큰 생성 (2단계 인증 완료)
    access_token = create_access_token(
        subject=str(user.id),
        roles=[user.roles],
        is_2fa_verified=True,
    )
    
    return {
        "access_token": access_token,
        "refresh_token": token_data.refresh_token,
        "token_type": "bearer",
        "requires_2fa": False,
    }