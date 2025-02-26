"""
데이터베이스 초기화
"""
import logging

from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.db import base  # noqa: F401
from app.models.user import UserRole

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    """
    데이터베이스 초기화 함수
    
    Args:
        db: 데이터베이스 세션
    """
    # 관리자 계정 생성
    admin_email = settings.FIRST_ADMIN_EMAIL
    admin_password = settings.FIRST_ADMIN_PASSWORD
    
    if not admin_email or not admin_password:
        logger.warning("관리자 계정 정보가 설정되지 않았습니다. 기본 관리자 계정을 생성합니다.")
        admin_email = "admin@example.com"
        admin_password = "admin123"
    
    # 관리자 계정이 이미 존재하는지 확인
    user = crud.user.get_by_email(db, email=admin_email)
    if not user:
        logger.info("관리자 계정을 생성합니다...")
        user_in = schemas.UserCreate(
            email=admin_email,
            username="admin",
            password=admin_password,
        )
        user = crud.user.create(db, obj_in=user_in)
        
        # 관리자 권한 부여
        user.roles = UserRole.ADMIN
        db.add(user)
        db.commit()
        logger.info("관리자 계정이 생성되었습니다.")
    else:
        logger.info("관리자 계정이 이미 존재합니다.") 