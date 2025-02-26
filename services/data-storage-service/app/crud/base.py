"""
CRUD 작업의 기본 클래스 정의
"""
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union, Sequence, cast

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

# 모델 타입 변수 정의
ModelType = TypeVar("ModelType", bound=Base)
# 생성 스키마 타입 변수 정의
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
# 업데이트 스키마 타입 변수 정의
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    CRUD 작업의 기본 클래스
    """
    def __init__(self, model: Type[ModelType]):
        """
        CRUD 모델 클래스 초기화
        
        Args:
            model: SQLAlchemy 모델 클래스
        """
        self.model = model
    
    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """
        ID로 객체 조회
        
        Args:
            db: 데이터베이스 세션
            id: 객체 ID
            
        Returns:
            조회된 객체 또는 None
        """
        # 타입 안전성을 위해 명시적으로 id 속성에 접근
        stmt = select(self.model).where(getattr(self.model, "id") == id)
        result = await db.execute(stmt)
        return result.scalars().first()
    
    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """
        여러 객체 조회
        
        Args:
            db: 데이터베이스 세션
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 객체 목록
        """
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        # Sequence를 List로 명시적 변환
        return list(result.scalars().all())
    
    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        """
        객체 생성
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 객체 데이터
            
        Returns:
            생성된 객체
        """
        obj_in_data = jsonable_encoder(obj_in)
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """
        객체 업데이트
        
        Args:
            db: 데이터베이스 세션
            db_obj: 업데이트할 데이터베이스 객체
            obj_in: 업데이트할 데이터
            
        Returns:
            업데이트된 객체
        """
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj
    
    async def remove(self, db: AsyncSession, *, id: int) -> ModelType:
        """
        객체 삭제
        
        Args:
            db: 데이터베이스 세션
            id: 삭제할 객체 ID
            
        Returns:
            삭제된 객체
        """
        obj = await self.get(db=db, id=id)
        if obj is None:
            raise ValueError(f"ID {id}인 객체를 찾을 수 없습니다")
        await db.delete(obj)
        await db.commit()
        return obj
    
    async def exists(self, db: AsyncSession, **kwargs) -> bool:
        """
        조건에 맞는 객체가 존재하는지 확인
        
        Args:
            db: 데이터베이스 세션
            **kwargs: 검색 조건
            
        Returns:
            객체 존재 여부
        """
        filters = [getattr(self.model, k) == v for k, v in kwargs.items()]
        result = await db.execute(select(self.model).filter(*filters))
        return result.first() is not None 