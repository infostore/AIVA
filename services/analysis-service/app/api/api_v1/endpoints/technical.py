"""
기술적 분석 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.config import settings
from app.schemas.technical import (
    MovingAverageResponse,
    RSIResponse,
    MACDResponse,
    BollingerBandsResponse
)

router = APIRouter()


@router.get("/moving-average/{stock_code}", response_model=MovingAverageResponse)
async def get_moving_average(
    stock_code: str,
    period: int = Query(settings.MOVING_AVERAGE_PERIODS[0], description="이동평균 기간 (일)"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 이동평균선 계산
    
    Args:
        stock_code: 주식 코드
        period: 이동평균 기간 (일)
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        MovingAverageResponse: 이동평균 데이터
    """
    if period not in settings.MOVING_AVERAGE_PERIODS:
        raise HTTPException(
            status_code=400,
            detail=f"지원되지 않는 이동평균 기간입니다. 지원되는 기간: {settings.MOVING_AVERAGE_PERIODS}"
        )
    
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 기본적으로 종료일로부터 설정된 기간의 2배 기간 동안의 데이터를 가져옴
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=period * 2)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {response.text}"
                )
            
            stock_data = response.json()
            
            if not stock_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 데이터가 없습니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 이동평균 계산
            df[f'ma_{period}'] = df['close_price'].rolling(window=period).mean()
            
            # NaN 값 제거
            df = df.dropna()
            
            # 응답 형식으로 변환
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "close_price": row['close_price'],
                    "ma_value": row[f'ma_{period}']
                })
            
            return {
                "stock_code": stock_code,
                "period": period,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"이동평균 계산 중 오류 발생: {str(e)}"
        )


@router.get("/rsi/{stock_code}", response_model=RSIResponse)
async def get_rsi(
    stock_code: str,
    period: int = Query(settings.RSI_PERIOD, description="RSI 계산 기간 (일)"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 RSI(Relative Strength Index) 계산
    
    Args:
        stock_code: 주식 코드
        period: RSI 계산 기간 (일)
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        RSIResponse: RSI 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # RSI 계산을 위해 더 많은 데이터가 필요함
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=period * 3)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {response.text}"
                )
            
            stock_data = response.json()
            
            if not stock_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 데이터가 없습니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 일일 변화량 계산
            df['price_change'] = df['close_price'].diff()
            
            # 상승/하락 분리
            df['gain'] = df['price_change'].apply(lambda x: x if x > 0 else 0)
            df['loss'] = df['price_change'].apply(lambda x: abs(x) if x < 0 else 0)
            
            # 평균 상승/하락 계산
            df['avg_gain'] = df['gain'].rolling(window=period).mean()
            df['avg_loss'] = df['loss'].rolling(window=period).mean()
            
            # RSI 계산
            df['rs'] = df['avg_gain'] / df['avg_loss']
            df['rsi'] = 100 - (100 / (1 + df['rs']))
            
            # NaN 값 제거
            df = df.dropna()
            
            # 응답 형식으로 변환
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "close_price": row['close_price'],
                    "rsi_value": row['rsi']
                })
            
            return {
                "stock_code": stock_code,
                "period": period,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"RSI 계산 중 오류 발생: {str(e)}"
        )


@router.get("/macd/{stock_code}", response_model=MACDResponse)
async def get_macd(
    stock_code: str,
    fast_period: int = Query(settings.MACD_FAST_PERIOD, description="빠른 EMA 기간"),
    slow_period: int = Query(settings.MACD_SLOW_PERIOD, description="느린 EMA 기간"),
    signal_period: int = Query(settings.MACD_SIGNAL_PERIOD, description="시그널 EMA 기간"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 MACD(Moving Average Convergence Divergence) 계산
    
    Args:
        stock_code: 주식 코드
        fast_period: 빠른 EMA 기간
        slow_period: 느린 EMA 기간
        signal_period: 시그널 EMA 기간
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        MACDResponse: MACD 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # MACD 계산을 위해 더 많은 데이터가 필요함
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=slow_period * 3)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {response.text}"
                )
            
            stock_data = response.json()
            
            if not stock_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 데이터가 없습니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # EMA 계산
            df['ema_fast'] = df['close_price'].ewm(span=fast_period, adjust=False).mean()
            df['ema_slow'] = df['close_price'].ewm(span=slow_period, adjust=False).mean()
            
            # MACD 라인 계산
            df['macd_line'] = df['ema_fast'] - df['ema_slow']
            
            # 시그널 라인 계산
            df['signal_line'] = df['macd_line'].ewm(span=signal_period, adjust=False).mean()
            
            # MACD 히스토그램 계산
            df['histogram'] = df['macd_line'] - df['signal_line']
            
            # NaN 값 제거
            df = df.dropna()
            
            # 응답 형식으로 변환
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "close_price": row['close_price'],
                    "macd_line": row['macd_line'],
                    "signal_line": row['signal_line'],
                    "histogram": row['histogram']
                })
            
            return {
                "stock_code": stock_code,
                "fast_period": fast_period,
                "slow_period": slow_period,
                "signal_period": signal_period,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"MACD 계산 중 오류 발생: {str(e)}"
        )


@router.get("/bollinger-bands/{stock_code}", response_model=BollingerBandsResponse)
async def get_bollinger_bands(
    stock_code: str,
    period: int = Query(settings.BOLLINGER_PERIOD, description="볼린저 밴드 기간"),
    std_dev: float = Query(settings.BOLLINGER_STD_DEV, description="표준편차 승수"),
    start_date: Optional[str] = Query(None, description="시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    주식의 볼린저 밴드 계산
    
    Args:
        stock_code: 주식 코드
        period: 볼린저 밴드 기간
        std_dev: 표준편차 승수
        start_date: 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        BollingerBandsResponse: 볼린저 밴드 데이터
    """
    # 날짜 설정
    if end_date is None:
        end_date = datetime.now().strftime("%Y-%m-%d")
    
    if start_date is None:
        # 볼린저 밴드 계산을 위해 더 많은 데이터가 필요함
        start_date_obj = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=period * 2)
        start_date = start_date_obj.strftime("%Y-%m-%d")
    
    try:
        # 데이터 스토리지 서비스에서 주가 데이터 가져오기
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/stock-prices/",
                params={
                    "stock_code": stock_code,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"데이터 스토리지 서비스 오류: {response.text}"
                )
            
            stock_data = response.json()
            
            if not stock_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 데이터가 없습니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 중간 밴드 (SMA) 계산
            df['middle_band'] = df['close_price'].rolling(window=period).mean()
            
            # 표준편차 계산
            df['std_dev'] = df['close_price'].rolling(window=period).std()
            
            # 상단 및 하단 밴드 계산
            df['upper_band'] = df['middle_band'] + (df['std_dev'] * std_dev)
            df['lower_band'] = df['middle_band'] - (df['std_dev'] * std_dev)
            
            # NaN 값 제거
            df = df.dropna()
            
            # 응답 형식으로 변환
            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": row['date'].strftime("%Y-%m-%d"),
                    "close_price": row['close_price'],
                    "upper_band": row['upper_band'],
                    "middle_band": row['middle_band'],
                    "lower_band": row['lower_band']
                })
            
            return {
                "stock_code": stock_code,
                "period": period,
                "std_dev": std_dev,
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"볼린저 밴드 계산 중 오류 발생: {str(e)}"
        ) 