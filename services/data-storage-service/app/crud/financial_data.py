"""
재무 데이터에 대한 CRUD 작업
"""
from datetime import date as date_type
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.stock_data import FinancialData, DataFrequency
from app.schemas.stock import FinancialDataCreate, FinancialDataUpdate


class CRUDFinancialData(CRUDBase[FinancialData, FinancialDataCreate, FinancialDataUpdate]):
    """
    재무 데이터에 대한 CRUD 작업 클래스
    """
    
    async def get_by_stock_id_and_period(
        self, db: AsyncSession, *, stock_id: int, period_end_date: date_type
    ) -> Optional[FinancialData]:
        """
        주식 ID와 기간 종료일로 재무 데이터 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            period_end_date: 기간 종료일
            
        Returns:
            조회된 재무 데이터 또는 None
        """
        result = await db.execute(
            select(self.model)
            .filter(
                self.model.stock_id == stock_id,
                self.model.period_end_date == period_end_date
            )
        )
        return result.scalars().first()
    
    async def get_multi_by_stock_id(
        self, db: AsyncSession, *, stock_id: int, skip: int = 0, limit: int = 100
    ) -> List[FinancialData]:
        """
        주식 ID로 재무 데이터 목록 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 재무 데이터 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.stock_id == stock_id)
            .order_by(self.model.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_multi_by_date_range(
        self, db: AsyncSession, *, stock_id: int, start_date: date_type, end_date: date_type
    ) -> List[FinancialData]:
        """
        날짜 범위로 재무 데이터 목록 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            조회된 재무 데이터 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(
                self.model.stock_id == stock_id,
                self.model.period_end_date >= start_date,
                self.model.period_end_date <= end_date
            )
            .order_by(self.model.period_end_date)
        )
        return list(result.scalars().all())
    
    async def get_latest_by_stock_id(
        self, db: AsyncSession, *, stock_id: int, frequency: Optional[DataFrequency] = None
    ) -> Optional[FinancialData]:
        """
        주식 ID로 최신 재무 데이터 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            frequency: 데이터 주기 (선택 사항)
            
        Returns:
            최신 재무 데이터 또는 None
        """
        query = select(self.model).filter(self.model.stock_id == stock_id)
        
        if frequency:
            query = query.filter(self.model.frequency == frequency)
            
        query = query.order_by(self.model.period_end_date.desc()).limit(1)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def get_multi_by_frequency(
        self, db: AsyncSession, *, stock_id: int, frequency: DataFrequency, skip: int = 0, limit: int = 100
    ) -> List[FinancialData]:
        """
        주기별 재무 데이터 목록 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            frequency: 데이터 주기
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 재무 데이터 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(
                self.model.stock_id == stock_id,
                self.model.frequency == frequency
            )
            .order_by(self.model.period_end_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create_or_update(
        self, db: AsyncSession, *, obj_in: FinancialDataCreate
    ) -> FinancialData:
        """
        재무 데이터 생성 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 재무 데이터
            
        Returns:
            생성 또는 업데이트된 재무 데이터
        """
        # 기존 데이터 조회
        existing = await self.get_by_stock_id_and_period(
            db=db, stock_id=obj_in.stock_id, period_end_date=obj_in.period_end_date
        )
        
        if existing:
            # 업데이트
            update_data = obj_in.model_dump(exclude={"stock_id", "period_end_date"})
            return await self.update(db=db, db_obj=existing, obj_in=update_data)
        else:
            # 생성
            return await self.create(db=db, obj_in=obj_in)
    
    async def bulk_create_or_update(
        self, db: AsyncSession, *, objs_in: List[FinancialDataCreate]
    ) -> List[FinancialData]:
        """
        재무 데이터 일괄 생성 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            objs_in: 생성할 재무 데이터 목록
            
        Returns:
            생성 또는 업데이트된 재무 데이터 목록
        """
        result = []
        for obj_in in objs_in:
            financial_data = await self.create_or_update(db=db, obj_in=obj_in)
            result.append(financial_data)
        return result


# CRUD 인스턴스 생성
financial_data = CRUDFinancialData(FinancialData) 