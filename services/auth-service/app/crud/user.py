"""
사용자 CRUD 작업
"""
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class UserCRUD:
    """
    사용자 CRUD 클래스
    """
    def get(self, db: Session, id: str) -> Optional[User]:
        """
        ID로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            id: 사용자 ID
            
        Returns:
            Optional[User]: 사용자 객체 또는 None
        """
        return db.query(User).filter(User.id == id).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """
        이메일로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            email: 사용자 이메일
            
        Returns:
            Optional[User]: 사용자 객체 또는 None
        """
        return db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """
        사용자명으로 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            username: 사용자명
            
        Returns:
            Optional[User]: 사용자 객체 또는 None
        """
        return db.query(User).filter(User.username == username).first()
    
    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """
        여러 사용자 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 최대 레코드 수
            
        Returns:
            List[User]: 사용자 목록
        """
        return db.query(User).offset(skip).limit(limit).all()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        사용자 생성
        
        Args:
            db: 데이터베이스 세션
            obj_in: 사용자 생성 스키마
            
        Returns:
            User: 생성된 사용자 객체
        """
        db_obj = User(
            email=obj_in.email,
            username=obj_in.username,
            hashed_password=get_password_hash(obj_in.password),
            roles=UserRole.USER,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """
        사용자 업데이트
        
        Args:
            db: 데이터베이스 세션
            db_obj: 기존 사용자 객체
            obj_in: 업데이트할 데이터
            
        Returns:
            User: 업데이트된 사용자 객체
        """
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, *, id: str) -> User:
        """
        사용자 삭제
        
        Args:
            db: 데이터베이스 세션
            id: 사용자 ID
            
        Returns:
            User: 삭제된 사용자 객체
        """
        obj = db.query(User).get(id)
        db.delete(obj)
        db.commit()
        return obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """
        사용자 인증
        
        Args:
            db: 데이터베이스 세션
            email: 사용자 이메일
            password: 비밀번호
            
        Returns:
            Optional[User]: 인증된 사용자 객체 또는 None
        """
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    def is_active(self, user: User) -> bool:
        """
        사용자 활성화 여부 확인
        
        Args:
            user: 사용자 객체
            
        Returns:
            bool: 활성화 여부
        """
        return user.is_active
    
    def is_admin(self, user: User) -> bool:
        """
        관리자 여부 확인
        
        Args:
            user: 사용자 객체
            
        Returns:
            bool: 관리자 여부
        """
        return user.roles == UserRole.ADMIN


# 사용자 CRUD 인스턴스 생성
user_crud = UserCRUD() 