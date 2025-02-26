"""
주식 정보에 대한 CRUD 작업
"""
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.stock_data import Stock
from app.schemas.stock import StockCreate, StockUpdate


class CRUDStock(CRUDBase[Stock, StockCreate, StockUpdate]):
    """
    주식 정보에 대한 CRUD 작업 클래스
    """
    
    async def get_by_symbol(self, db: AsyncSession, *, symbol: str) -> Optional[Stock]:
        """
        심볼로 주식 정보 조회
        
        Args:
            db: 데이터베이스 세션
            symbol: 주식 심볼
            
        Returns:
            조회된 주식 정보 또는 None
        """
        result = await db.execute(select(self.model).filter(self.model.symbol == symbol))
        return result.scalars().first()
    
    async def get_multi_by_exchange(
        self, db: AsyncSession, *, exchange: str, skip: int = 0, limit: int = 100
    ) -> List[Stock]:
        """
        거래소별 주식 정보 목록 조회
        
        Args:
            db: 데이터베이스 세션
            exchange: 거래소 이름
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 주식 정보 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.exchange == exchange)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_multi_by_sector(
        self, db: AsyncSession, *, sector: str, skip: int = 0, limit: int = 100
    ) -> List[Stock]:
        """
        섹터별 주식 정보 목록 조회
        
        Args:
            db: 데이터베이스 세션
            sector: 섹터 이름
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 주식 정보 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.sector == sector)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_multi_by_country(
        self, db: AsyncSession, *, country: str, skip: int = 0, limit: int = 100
    ) -> List[Stock]:
        """
        국가별 주식 정보 목록 조회
        
        Args:
            db: 데이터베이스 세션
            country: 국가 이름
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            조회된 주식 정보 목록
        """
        result = await db.execute(
            select(self.model)
            .filter(self.model.country == country)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def search(
        self, db: AsyncSession, *, query: str, skip: int = 0, limit: int = 100
    ) -> List[Stock]:
        """
        주식 정보 검색
        
        Args:
            db: 데이터베이스 세션
            query: 검색어
            skip: 건너뛸 레코드 수
            limit: 최대 반환 레코드 수
            
        Returns:
            검색된 주식 정보 목록
        """
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(self.model)
            .filter(
                (self.model.symbol.ilike(search_pattern)) |
                (self.model.name.ilike(search_pattern))
            )
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# CRUD 인스턴스 생성
stock = CRUDStock(Stock) 