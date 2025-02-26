"""
재무 데이터 엔드포인트
"""
from datetime import date as date_type
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.db.session import get_db
from app.models.stock_data import DataFrequency
from app.schemas.stock import FinancialData, FinancialDataCreate, FinancialDataUpdate

router = APIRouter()


@router.get("/stock/{stock_id}", response_model=List[FinancialData])
async def read_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    skip: int = 0,
    limit: int = 100,
    frequency: Optional[DataFrequency] = None,
):
    """
    주식 ID로 재무 데이터 목록 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        skip: 건너뛸 레코드 수
        limit: 최대 반환 레코드 수
        frequency: 데이터 주기 필터
        
    Returns:
        재무 데이터 목록
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    if frequency:
        financials = await crud.financial_data.get_multi_by_frequency(
            db=db, stock_id=stock_id, frequency=frequency, skip=skip, limit=limit
        )
    else:
        financials = await crud.financial_data.get_multi_by_stock_id(
            db=db, stock_id=stock_id, skip=skip, limit=limit
        )
    return financials


@router.get("/stock/{stock_id}/latest", response_model=FinancialData)
async def read_latest_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    frequency: Optional[DataFrequency] = None,
):
    """
    주식 ID로 최신 재무 데이터 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        frequency: 데이터 주기 필터
        
    Returns:
        최신 재무 데이터
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    financial = await crud.financial_data.get_latest_by_stock_id(
        db=db, stock_id=stock_id, frequency=frequency
    )
    if not financial:
        raise HTTPException(status_code=404, detail="재무 데이터를 찾을 수 없습니다")
    return financial


@router.get("/stock/{stock_id}/range", response_model=List[FinancialData])
async def read_financial_data_by_date_range(
    *,
    db: AsyncSession = Depends(get_db),
    stock_id: int,
    start_date: date_type,
    end_date: date_type,
):
    """
    날짜 범위로 재무 데이터 목록 조회
    
    Args:
        db: 데이터베이스 세션
        stock_id: 주식 ID
        start_date: 시작 날짜
        end_date: 종료 날짜
        
    Returns:
        재무 데이터 목록
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    financials = await crud.financial_data.get_multi_by_date_range(
        db=db, stock_id=stock_id, start_date=start_date, end_date=end_date
    )
    return financials


@router.post("/", response_model=FinancialData)
async def create_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    financial_in: FinancialDataCreate,
):
    """
    재무 데이터 생성
    
    Args:
        db: 데이터베이스 세션
        financial_in: 생성할 재무 데이터
        
    Returns:
        생성된 재무 데이터
    """
    # 주식 존재 여부 확인
    stock = await crud.stock.get(db=db, id=financial_in.stock_id)
    if not stock:
        raise HTTPException(status_code=404, detail="주식을 찾을 수 없습니다")
    
    # 기존 데이터 확인
    existing = await crud.financial_data.get_by_stock_id_and_period(
        db=db, stock_id=financial_in.stock_id, period_end_date=financial_in.period_end_date
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"해당 기간({financial_in.period_end_date})의 재무 데이터가 이미 존재합니다",
        )
    
    financial = await crud.financial_data.create(db=db, obj_in=financial_in)
    return financial


@router.put("/{financial_id}", response_model=FinancialData)
async def update_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    financial_id: int,
    financial_in: FinancialDataUpdate,
):
    """
    재무 데이터 업데이트
    
    Args:
        db: 데이터베이스 세션
        financial_id: 재무 데이터 ID
        financial_in: 업데이트할 재무 데이터
        
    Returns:
        업데이트된 재무 데이터
    """
    financial = await crud.financial_data.get(db=db, id=financial_id)
    if not financial:
        raise HTTPException(status_code=404, detail="재무 데이터를 찾을 수 없습니다")
    
    financial = await crud.financial_data.update(db=db, db_obj=financial, obj_in=financial_in)
    return financial


@router.delete("/{financial_id}", response_model=FinancialData)
async def delete_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    financial_id: int,
):
    """
    재무 데이터 삭제
    
    Args:
        db: 데이터베이스 세션
        financial_id: 재무 데이터 ID
        
    Returns:
        삭제된 재무 데이터
    """
    financial = await crud.financial_data.get(db=db, id=financial_id)
    if not financial:
        raise HTTPException(status_code=404, detail="재무 데이터를 찾을 수 없습니다")
    
    financial = await crud.financial_data.remove(db=db, id=financial_id)
    return financial


@router.post("/bulk", response_model=List[FinancialData])
async def create_bulk_financial_data(
    *,
    db: AsyncSession = Depends(get_db),
    financials_in: List[FinancialDataCreate],
):
    """
    재무 데이터 일괄 생성
    
    Args:
        db: 데이터베이스 세션
        financials_in: 생성할 재무 데이터 목록
        
    Returns:
        생성된 재무 데이터 목록
    """
    # 모든 주식 ID 수집
    stock_ids = set(financial.stock_id for financial in financials_in)
    
    # 주식 존재 여부 확인
    for stock_id in stock_ids:
        stock = await crud.stock.get(db=db, id=stock_id)
        if not stock:
            raise HTTPException(status_code=404, detail=f"주식 ID {stock_id}를 찾을 수 없습니다")
    
    financials = await crud.financial_data.bulk_create_or_update(db=db, objs_in=financials_in)
    return financials 