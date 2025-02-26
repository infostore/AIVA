"""
주식 가격 데이터 엔드포인트
"""
from datetime import date as date_type
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db.session import get_db
from app.models.stock_data import DataFrequency
from app.schemas.stock import StockPrice, StockPriceCreate, StockPriceUpdate

router = APIRouter()


@router.get("/stock/{stock_id}", response_model=List[StockPrice])
async def read_stock_prices(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    skip: int = 0,
    limit: int = 100,
):
    """
    주식 ID로 가격 데이터 목록 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        skip: 건너뛸 레코드 수
        limit: 최대 반환 레코드 수
        
    Returns:
        가격 데이터 목록
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    prices = await crud.stock_price.get_multi_by_stock_id(
        db=db, stock_id=stock_id, skip=skip, limit=limit
    )
    return prices


@router.get("/stock/{stock_id}/latest", response_model=StockPrice)
async def read_latest_stock_price(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
):
    """
    주식 ID로 최신 가격 데이터 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        
    Returns:
        최신 가격 데이터
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    price = await crud.stock_price.get_latest_by_stock_id(db=db, stock_id=stock_id)
    if not price:
        raise HTTPException(status_code=404, detail="가격 데이터를 찾을 수 없습니다")
    return price


@router.get("/stock/{stock_id}/range", response_model=List[StockPrice])
async def read_stock_prices_by_date_range(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    start_date: date_type,
    end_date: date_type,
):
    """
    날짜 범위로 가격 데이터 목록 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        start_date: 시작 날짜
        end_date: 종료 날짜
        
    Returns:
        가격 데이터 목록
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    prices = await crud.stock_price.get_multi_by_date_range(
        db=db, stock_id=stock_id, start_date=start_date, end_date=end_date
    )
    return prices


@router.get("/stock/{stock_id}/stats")
async def read_stock_price_stats(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    start_date: date_type,
    end_date: date_type,
):
    """
    주식 가격 통계 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        start_date: 시작 날짜
        end_date: 종료 날짜
        
    Returns:
        가격 통계 정보
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    min_price, max_price, avg_close, avg_volume, count = await crud.stock_price.get_price_stats(
        db=db, stock_id=stock_id, start_date=start_date, end_date=end_date
    )
    
    return {
        "min_price": min_price,
        "max_price": max_price,
        "avg_close": avg_close,
        "avg_volume": avg_volume,
        "count": count
    }


@router.post("/", response_model=StockPrice)
async def create_stock_price(
    *,
    db: AsyncSession = Depends(get_db),
    price_in: StockPriceCreate,
):
    """
    가격 데이터 생성
    
    Args:
        db: 데이터베이스 세션
        price_in: 생성할 가격 데이터
        
    Returns:
        생성된 가격 데이터
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=price_in.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    # 기존 데이터 확인
    existing = await crud.stock_price.get_by_stock_id_and_date(
        db=db, stock_id=price_in.stock_id, date=price_in.date
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"해당 날짜({price_in.date})의 가격 데이터가 이미 존재합니다",
        )
    
    price = await crud.stock_price.create(db=db, obj_in=price_in)
    return price


@router.put("/{price_id}", response_model=StockPrice)
async def update_stock_price(
    *,
    db: AsyncSession = Depends(get_db),
    price_id: int,
    price_in: StockPriceUpdate,
):
    """
    가격 데이터 업데이트
    
    Args:
        db: 데이터베이스 세션
        price_id: 가격 데이터 ID
        price_in: 업데이트할 가격 데이터
        
    Returns:
        업데이트된 가격 데이터
    """
    price = await crud.stock_price.get(db=db, id=price_id)
    if not price:
        raise HTTPException(status_code=404, detail="가격 데이터를 찾을 수 없습니다")
    
    price = await crud.stock_price.update(db=db, db_obj=price, obj_in=price_in)
    return price


@router.delete("/{price_id}", response_model=StockPrice)
async def delete_stock_price(
    *,
    db: AsyncSession = Depends(get_db),
    price_id: int,
):
    """
    가격 데이터 삭제
    
    Args:
        db: 데이터베이스 세션
        price_id: 가격 데이터 ID
        
    Returns:
        삭제된 가격 데이터
    """
    price = await crud.stock_price.get(db=db, id=price_id)
    if not price:
        raise HTTPException(status_code=404, detail="가격 데이터를 찾을 수 없습니다")
    
    price = await crud.stock_price.remove(db=db, id=price_id)
    return price


@router.post("/bulk", response_model=List[StockPrice])
async def create_bulk_stock_prices(
    *,
    db: AsyncSession = Depends(get_db),
    prices_in: List[StockPriceCreate],
):
    """
    가격 데이터 일괄 생성
    
    Args:
        db: 데이터베이스 세션
        prices_in: 생성할 가격 데이터 목록
        
    Returns:
        생성된 가격 데이터 목록
    """
    # 모든 주식 ID 수집
    stock_ids = set(price.stock_id for price in prices_in)
    
    # 주식 존재 여부 확인
    for stock_id in stock_ids:
        stock = await crud.stock.get(db=db, id=stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail=f"주식 ID {stock_id}를 찾을 수 없습니다")
    
    prices = await crud.stock_price.bulk_create_or_update(db=db, objs_in=prices_in)
    return prices 