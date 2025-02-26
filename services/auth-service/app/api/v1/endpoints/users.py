"""
사용자 관련 API 엔드포인트
"""
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.api import deps
from app.core.security import get_password_hash
from app.models.user import User, UserRole

router = APIRouter()


@router.get("/me", response_model=schemas.user.User)
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user


@router.put("/me", response_model=schemas.user.User)
def update_user_me(
    user_in: schemas.user.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    현재 로그인한 사용자 정보 업데이트
    """
    user = crud.user.update(db, db_obj=current_user, obj_in=user_in)
    return user


@router.put("/me/password", response_model=schemas.user.User)
def update_password(
    password_in: schemas.user.UserPasswordUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    현재 로그인한 사용자 비밀번호 변경
    """
    # 현재 비밀번호 확인
    if not crud.user.authenticate(
        db, email=current_user.email, password=password_in.current_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="현재 비밀번호가 올바르지 않습니다",
        )
    
    # 새 비밀번호 확인
    if password_in.new_password != password_in.new_password_confirm:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="새 비밀번호가 일치하지 않습니다",
        )
    
    # 비밀번호 업데이트
    hashed_password = get_password_hash(password_in.new_password)
    current_user.hashed_password = hashed_password
    db.add(current_user)
    db.commit()
    
    return current_user


@router.get("", response_model=List[schemas.user.User])
def read_users(
    db: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(deps.check_admin_permission),
) -> Any:
    """
    사용자 목록 조회 (관리자 전용)
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("", response_model=schemas.user.User)
def create_user(
    user_in: schemas.user.UserCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_admin_permission),
) -> Any:
    """
    새 사용자 생성 (관리자 전용)
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
    
    # 사용자 생성
    user = crud.user.create(db, obj_in=user_in)
    return user


@router.get("/{user_id}", response_model=schemas.user.User)
def read_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_admin_permission),
) -> Any:
    """
    특정 사용자 정보 조회 (관리자 전용)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    return user


@router.put("/{user_id}", response_model=schemas.user.User)
def update_user(
    user_id: str,
    user_in: schemas.user.UserUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_admin_permission),
) -> Any:
    """
    특정 사용자 정보 업데이트 (관리자 전용)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)
    return user


@router.delete("/{user_id}", response_model=schemas.user.User)
def delete_user(
    user_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.check_admin_permission),
) -> Any:
    """
    특정 사용자 삭제 (관리자 전용)
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자를 찾을 수 없습니다",
        )
    user = crud.user.delete(db, id=user_id)
    return user