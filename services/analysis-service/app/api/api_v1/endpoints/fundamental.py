"""
기본적 분석 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import httpx
from datetime import datetime, timedelta

from app.config import settings
from app.schemas.fundamental import (
    PERResponse,
    PBRResponse,
    ROEResponse,
    DividendYieldResponse
)

router = APIRouter()


@router.get("/per/{stock_code}", response_model=PERResponse)
async def get_per(
    stock_code: str,
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 PER(Price-to-Earnings Ratio) 계산
    
    Args:
        stock_code: 주식 코드
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        PERResponse: PER 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 기본적으로 1년 데이터
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            price_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if price_response.status_code != 200:
                raise HTTPException(
                    status_code=price_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {price_response.text}"
                )
            
            price_data = price_response.json()
            
            if not price_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 가격 데이터가 없습니다."
                )
            
            # 재무 데이터 가져오기
            financial_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/financials/{stock_code}"
            )
            
            if financial_response.status_code != 200:
                raise HTTPException(
                    status_code=financial_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {financial_response.text}"
                )
            
            financial_data = financial_response.json()
            
            if not financial_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 재무 데이터가 없습니다."
                )
            
            # PER 계산
            result = []
            for price_item in price_data:
                price_date = datetime.strptime(price_item['date'], "%Y-%m-%d")
                
                # 해당 날짜에 가장 가까운 재무 데이터 찾기
                closest_financial = None
                min_diff = float('inf')
                
                for financial_item in financial_data:
                    financial_date = datetime.strptime(financial_item['date'], "%Y-%m-%d")
                    diff = abs((price_date - financial_date).days)
                    
                    # 가장 최근의 재무 데이터 사용 (과거 데이터만)
                    if diff < min_diff and financial_date <= price_date:
                        min_diff = diff
                        closest_financial = financial_item
                
                if closest_financial and closest_financial['eps'] > 0:
                    per = price_item['close_price'] / closest_financial['eps']
                    result.append({
                        "date": price_item['date'],
                        "close_price": price_item['close_price'],
                        "eps": closest_financial['eps'],
                        "per": per
                    })
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 PER을 계산할 수 없습니다. EPS가 0이거나 음수일 수 있습니다."
                )
            
            return {
                "stock_code": stock_code,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PER 계산 중 오류 발생: {str(e)}"
        )


@router.get("/pbr/{stock_code}", response_model=PBRResponse)
async def get_pbr(
    stock_code: str,
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 PBR(Price-to-Book Ratio) 계산
    
    Args:
        stock_code: 주식 코드
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        PBRResponse: PBR 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 기본적으로 1년 데이터
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            price_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if price_response.status_code != 200:
                raise HTTPException(
                    status_code=price_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {price_response.text}"
                )
            
            price_data = price_response.json()
            
            if not price_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 가격 데이터가 없습니다."
                )
            
            # 재무 데이터 가져오기
            financial_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/financials/{stock_code}"
            )
            
            if financial_response.status_code != 200:
                raise HTTPException(
                    status_code=financial_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {financial_response.text}"
                )
            
            financial_data = financial_response.json()
            
            if not financial_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 재무 데이터가 없습니다."
                )
            
            # PBR 계산
            result = []
            for price_item in price_data:
                price_date = datetime.strptime(price_item['date'], "%Y-%m-%d")
                
                # 해당 날짜에 가장 가까운 재무 데이터 찾기
                closest_financial = None
                min_diff = float('inf')
                
                for financial_item in financial_data:
                    financial_date = datetime.strptime(financial_item['date'], "%Y-%m-%d")
                    diff = abs((price_date - financial_date).days)
                    
                    # 가장 최근의 재무 데이터 사용 (과거 데이터만)
                    if diff < min_diff and financial_date <= price_date:
                        min_diff = diff
                        closest_financial = financial_item
                
                if closest_financial and closest_financial['bps'] > 0:
                    pbr = price_item['close_price'] / closest_financial['bps']
                    result.append({
                        "date": price_item['date'],
                        "close_price": price_item['close_price'],
                        "bps": closest_financial['bps'],
                        "pbr": pbr
                    })
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 PBR을 계산할 수 없습니다. BPS가 0이거나 음수일 수 있습니다."
                )
            
            return {
                "stock_code": stock_code,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"PBR 계산 중 오류 발생: {str(e)}"
        )


@router.get("/roe/{stock_code}", response_model=ROEResponse)
async def get_roe(
    stock_code: str,
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 ROE(Return on Equity) 계산
    
    Args:
        stock_code: 주식 코드
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        ROEResponse: ROE 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 기본적으로 3년 데이터
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365 * 3)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 재무 데이터 가져오기
        async with httpx.AsyncClient() as client:
            financial_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/financials/{stock_code}"
            )
            
            if financial_response.status_code != 200:
                raise HTTPException(
                    status_code=financial_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {financial_response.text}"
                )
            
            financial_data = financial_response.json()
            
            if not financial_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 재무 데이터가 없습니다."
                )
            
            # 날짜 필터링
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d")
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
            
            filtered_data = []
            for item in financial_data:
                item_date = datetime.strptime(item['date'], "%Y-%m-%d")
                if start_date_obj <= item_date <= end_date_obj:
                    filtered_data.append(item)
            
            if not filtered_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 지정된 기간 내 재무 데이터가 없습니다."
                )
            
            # ROE 계산
            result = []
            for item in filtered_data:
                if item['equity'] > 0:
                    roe = (item['net_income'] / item['equity']) * 100
                    result.append({
                        "date": item['date'],
                        "net_income": item['net_income'],
                        "equity": item['equity'],
                        "roe": roe
                    })
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 ROE를 계산할 수 없습니다. 자본이 0이거나 음수일 수 있습니다."
                )
            
            return {
                "stock_code": stock_code,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ROE 계산 중 오류 발생: {str(e)}"
        )


@router.get("/dividend-yield/{stock_code}", response_model=DividendYieldResponse)
async def get_dividend_yield(
    stock_code: str,
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 배당 수익률 계산
    
    Args:
        stock_code: 주식 코드
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        DividendYieldResponse: 배당 수익률 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 기본적으로 5년 데이터
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=365 * 5)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            price_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if price_response.status_code != 200:
                raise HTTPException(
                    status_code=price_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {price_response.text}"
                )
            
            price_data = price_response.json()
            
            if not price_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 가격 데이터가 없습니다."
                )
            
            # 재무 데이터 가져오기
            financial_response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/financials/{stock_code}"
            )
            
            if financial_response.status_code != 200:
                raise HTTPException(
                    status_code=financial_response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {financial_response.text}"
                )
            
            financial_data = financial_response.json()
            
            if not financial_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 재무 데이터가 없습니다."
                )
            
            # 배당 수익률 계산
            result = []
            for price_item in price_data:
                price_date = datetime.strptime(price_item['date'], "%Y-%m-%d")
                
                # 해당 날짜에 가장 가까운 재무 데이터 찾기
                closest_financial = None
                min_diff = float('inf')
                
                for financial_item in financial_data:
                    financial_date = datetime.strptime(financial_item['date'], "%Y-%m-%d")
                    diff = abs((price_date - financial_date).days)
                    
                    # 가장 최근의 재무 데이터 사용 (과거 데이터만)
                    if diff < min_diff and financial_date <= price_date:
                        min_diff = diff
                        closest_financial = financial_item
                
                if closest_financial and closest_financial['dividend_per_share'] > 0:
                    dividend_yield = (closest_financial['dividend_per_share'] / price_item['close_price']) * 100
                    result.append({
                        "date": price_item['date'],
                        "close_price": price_item['close_price'],
                        "dividend_per_share": closest_financial['dividend_per_share'],
                        "dividend_yield": dividend_yield
                    })
            
            if not result:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 배당 수익률을 계산할 수 없습니다. 배당금이 0이거나 데이터가 없을 수 있습니다."
                )
            
            return {
                "stock_code": stock_code,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"배당 수익률 계산 중 오류 발생: {str(e)}"
        ) 