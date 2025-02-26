"""
주식 가격 데이터에 대한 CRUD 작업
"""
from datetime import date as date_type
from typing import List, Optional, Tuple

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.stock_data import StockPrice, DataFrequency
from app.schemas.stock import StockPriceCreate, StockPriceUpdate


class CRUDStockPrice(CRUDBase[StockPrice, StockPriceCreate, StockPriceUpdate]):
    """
    주식 가격 데이터에 대한 CRUD 작업 클래스
    """
    
    async def get_by_stock_id_and_date(
        self, db: AsyncSession, *, stock_id: int, date: date_type
    ) -> Optional[StockPrice]:
        """
        주식 ID와 날짜로 가격 데이터 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            date: 날짜
            
        Returns:
            조회된 가격 데이터 또는 None
        """
        result = await db.execute(
            select(self.model)
            .filter(
                self.model.stock_id == stock_id,
                self.model.date == date
            )
        )
        return result.scalars().first()
    
    async def get_multi_by_stock_id(
        self, db: AsyncSession, *, stock_id: int, skip: int = 0, limit: int = 100
    ) -> List[StockPrice]:
        """
        주식 ID로 가격 데이터 목록 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 가격 데이터 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.stock_id == stock_id)
            .order_by(self.model.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_multi_by_date_range(
        self, db: AsyncSession, *, stock_id: int, start_date: date_type, end_date: date_type
    ) -> List[StockPrice]:
        """
        날짜 범위로 가격 데이터 목록 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            조회된 가격 데이터 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(
                self.model.stock_id == stock_id,
                self.model.date >= start_date,
                self.model.date <= end_date
            )
            .order_by(self.model.date)
        )
        return list(result.scalars().all())
    
    async def get_latest_by_stock_id(
        self, db: AsyncSession, *, stock_id: int
    ) -> Optional[StockPrice]:
        """
        주식 ID로 최신 가격 데이터 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            
        Returns:
            최신 가격 데이터 또는 None
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.stock_id == stock_id)
            .order_by(self.model.date.desc())
            .limit(1)
        )
        return result.scalars().first()
    
    async def get_price_stats(
        self, db: AsyncSession, *, stock_id: int, start_date: date_type, end_date: date_type
    ) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float], Optional[int]]:
        """
        주식 가격 통계 조회
        
        Args:
            db: 데이터베이스 세션
            stock_id: 주식 ID
            start_date: 시작 날짜
            end_date: 종료 날짜
            
        Returns:
            (최저가, 최고가, 평균 종가, 평균 거래량, 데이터 수) 튜플
        """
        result = await db.execute(
            select(
                func.min(self.model.low),
                func.max(self.model.high),
                func.avg(self.model.close),
                func.avg(self.model.volume),
                func.count()
            )
            .filter(
                self.model.stock_id == stock_id,
                self.model.date >= start_date,
                self.model.date <= end_date
            )
        )
        return result.one()
    
    async def create_or_update(
        self, db: AsyncSession, *, obj_in: StockPriceCreate
    ) -> StockPrice:
        """
        가격 데이터 생성 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            obj_in: 생성할 가격 데이터
            
        Returns:
            생성 또는 업데이트된 가격 데이터
        """
        # 기존 데이터 조회
        existing = await self.get_by_stock_id_and_date(
            db=db, stock_id=obj_in.stock_id, date=obj_in.date
        )
        
        if existing:
            # 업데이트
            update_data = obj_in.model_dump(exclude={"stock_id", "date"})
            return await self.update(db=db, db_obj=existing, obj_in=update_data)
        else:
            # 생성
            return await self.create(db=db, obj_in=obj_in)
    
    async def bulk_create_or_update(
        self, db: AsyncSession, *, objs_in: List[StockPriceCreate]
    ) -> List[StockPrice]:
        """
        가격 데이터 일괄 생성 또는 업데이트
        
        Args:
            db: 데이터베이스 세션
            objs_in: 생성할 가격 데이터 목록
            
        Returns:
            생성 또는 업데이트된 가격 데이터 목록
        """
        result = []
        for obj_in in objs_in:
            price = await self.create_or_update(db=db, obj_in=obj_in)
            result.append(price)
        return result


# CRUD 인스턴스 생성
stock_price = CRUDStockPrice(StockPrice) 