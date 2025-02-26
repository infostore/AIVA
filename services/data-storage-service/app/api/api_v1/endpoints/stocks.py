"""
주식 정보 엔드포인트
"""
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db.session import get_db
from app.schemas.stock import Stock, StockCreate, StockUpdate, StockWithoutData

router = APIRouter()


@router.get("/", response_model=List[StockWithoutData])
async def read_stocks(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    exchange: Optional[str] = None,
    sector: Optional[str] = None,
    country: Optional[str] = None,
    search: Optional[str] = None,
):
    """
    주식 정보 목록 조회
    
    Args:
        db: 데이터베이스 세션
        skip: 건너뛸 레코드 수
        limit: 최대 반환 레코드 수
        exchange: 거래소 필터
        sector: 섹터 필터
        country: 국가 필터
        search: 검색어
        
    Returns:
        주식 정보 목록
    """
    if search:
        stocks = await crud.stock.search(db=db, query=search, skip=skip, limit=limit)
    elif exchange:
        stocks = await crud.stock.get_multi_by_exchange(db=db, exchange=exchange, skip=skip, limit=limit)
    elif sector:
        stocks = await crud.stock.get_multi_by_sector(db=db, sector=sector, skip=skip, limit=limit)
    elif country:
        stocks = await crud.stock.get_multi_by_country(db=db, country=country, skip=skip, limit=limit)
    else:
        stocks = await crud.stock.get_multi(db=db, skip=skip, limit=limit)
    return stocks


@router.post("/", response_model=Stock)
async def create_stock(
    *,
    db: AsyncSession = Depends(get_db),
    stock_in: StockCreate,
):
    """
    주식 정보 생성
    
    Args:
        db: 데이터베이스 세션
        stock_in: 생성할 주식 정보
        
    Returns:
        생성된 주식 정보
    """
    stock = await crud.stock.get_by_symbol(db=db, symbol=stock_in.symbol)
    if stock:
        raise HTTPException(
            status_code=400,
            detail=f"Symbol {stock_in.symbol}은(는) 이미 존재합니다",
        )
    stock = await crud.stock.create(db=db, obj_in=stock_in)
    return stock


@router.get("/{stock_id}", response_model=Stock)
async def read_stock(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
):
    """
    주식 정보 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        
    Returns:
        조회된 주식 정보
    """
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return stock


@router.get("/symbol/{symbol}", response_model=Stock)
async def read_stock_by_symbol(
    *,
    db: AsyncSession = Depends(get_db),
    symbol: str,
):
    """
    심볼로 주식 정보 조회
    
    Args:
        db: 데이터베이스 세션
        symbol: 주식 심볼
        
    Returns:
        조회된 주식 정보
    """
    stock = await crud.stock.get_by_symbol(db=db, symbol=symbol)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    return stock


@router.put("/{stock_id}", response_model=Stock)
async def update_stock(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    stock_in: StockUpdate,
):
    """
    주식 정보 업데이트
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        stock_in: 업데이트할 주식 정보
        
    Returns:
        업데이트된 주식 정보
    """
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    stock = await crud.stock.update(db=db, db_obj=stock, obj_in=stock_in)
    return stock


@router.delete("/{stock_id}", response_model=Stock)
async def delete_stock(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
):
    """
    주식 정보 삭제
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        
    Returns:
        삭제된 주식 정보
    """
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    stock = await crud.stock.remove(db=db, id=stock_id)
    return stock 