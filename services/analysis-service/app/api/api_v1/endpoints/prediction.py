"""
예측 엔드포인트
"""
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
import httpx
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from statsmodels.tsa.arima.model import ARIMA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.schemas.prediction import (
    ARIMAPredictionResponse,
    LinearRegressionPredictionResponse
)

router = APIRouter()


@router.get("/arima/{stock_code}", response_model=ARIMAPredictionResponse)
async def get_arima_prediction(
    stock_code: str,
    days_to_predict: int = Query(7, description="예측할 일수"),
    start_date: Optional[str] = Query(None, description="학습 데이터 시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="학습 데이터 종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    ARIMA 모델을 사용한 주가 예측
    
    Args:
        stock_code: 주식 코드
        days_to_predict: 예측할 일수
        start_date: 학습 데이터 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 학습 데이터 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        ARIMAPredictionResponse: ARIMA 예측 결과
    """
    if days_to_predict <= 0 or days_to_predict > 30:
        raise HTTPException(
            status_code=400,
            detail="예측 일수는 1에서 30 사이여야 합니다."
        )
    
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
            
            if not stock_data or len(stock_data) < 30:  # 최소 30일 데이터 필요
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 충분한 데이터가 없습니다. 최소 30일 이상의 데이터가 필요합니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # ARIMA 모델 학습 (간단한 모델 사용)
            model = ARIMA(df['close_price'].values, order=(5, 1, 0))
            model_fit = model.fit()
            
            # 예측
            forecast = model_fit.forecast(steps=days_to_predict)
            
            # 예측 날짜 생성
            last_date = df['date'].iloc[-1]
            prediction_dates = []
            for i in range(1, days_to_predict + 1):
                next_date = last_date + timedelta(days=i)
                # 주말 건너뛰기
                while next_date.weekday() >= 5:  # 5: 토요일, 6: 일요일
                    next_date += timedelta(days=1)
                prediction_dates.append(next_date)
            
            # 응답 형식으로 변환
            result = []
            for i, date in enumerate(prediction_dates):
                if i < len(forecast):
                    result.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "predicted_price": float(forecast[i])
                    })
            
            return {
                "stock_code": stock_code,
                "model": "ARIMA(5,1,0)",
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"ARIMA 예측 중 오류 발생: {str(e)}"
        )


@router.get("/linear-regression/{stock_code}", response_model=LinearRegressionPredictionResponse)
async def get_linear_regression_prediction(
    stock_code: str,
    days_to_predict: int = Query(7, description="예측할 일수"),
    start_date: Optional[str] = Query(None, description="학습 데이터 시작 날짜 (YYYY-MM-DD 형식)"),
    end_date: Optional[str] = Query(None, description="학습 데이터 종료 날짜 (YYYY-MM-DD 형식)")
):
    """
    선형 회귀를 사용한 주가 예측
    
    Args:
        stock_code: 주식 코드
        days_to_predict: 예측할 일수
        start_date: 학습 데이터 시작 날짜 (YYYY-MM-DD 형식)
        end_date: 학습 데이터 종료 날짜 (YYYY-MM-DD 형식)
        
    Returns:
        LinearRegressionPredictionResponse: 선형 회귀 예측 결과
    """
    if days_to_predict <= 0 or days_to_predict > 30:
        raise HTTPException(
            status_code=400,
            detail="예측 일수는 1에서 30 사이여야 합니다."
        )
    
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
            
            if not stock_data or len(stock_data) < 30:  # 최소 30일 데이터 필요
                raise HTTPException(
                    status_code=404,
                    detail=f"주식 코드 {stock_code}에 대한 충분한 데이터가 없습니다. 최소 30일 이상의 데이터가 필요합니다."
                )
            
            # 데이터프레임으로 변환
            df = pd.DataFrame(stock_data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            # 특성 생성
            df['day_index'] = range(len(df))
            
            # 이동평균 추가
            df['ma_5'] = df['close_price'].rolling(window=5).mean()
            df['ma_10'] = df['close_price'].rolling(window=10).mean()
            df['ma_20'] = df['close_price'].rolling(window=20).mean()
            
            # 변동성 추가
            df['volatility'] = df['close_price'].rolling(window=10).std()
            
            # NaN 값 제거
            df = df.dropna()
            
            if len(df) < 20:
                raise HTTPException(
                    status_code=404,
                    detail=f"특성 생성 후 충분한 데이터가 없습니다."
                )
            
            # 특성 및 타겟 분리
            X = df[['day_index', 'ma_5', 'ma_10', 'ma_20', 'volatility']].values
            y = df['close_price'].values
            
            # 스케일링
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
            
            X_scaled = scaler_X.fit_transform(X)
            y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).flatten()
            
            # 모델 학습
            model = LinearRegression()
            model.fit(X_scaled, y_scaled)
            
            # 예측 날짜 생성
            last_date = df['date'].iloc[-1]
            prediction_dates = []
            for i in range(1, days_to_predict + 1):
                next_date = last_date + timedelta(days=i)
                # 주말 건너뛰기
                while next_date.weekday() >= 5:  # 5: 토요일, 6: 일요일
                    next_date += timedelta(days=1)
                prediction_dates.append(next_date)
            
            # 예측을 위한 특성 생성
            last_day_index = df['day_index'].iloc[-1]
            last_ma_5 = df['ma_5'].iloc[-1]
            last_ma_10 = df['ma_10'].iloc[-1]
            last_ma_20 = df['ma_20'].iloc[-1]
            last_volatility = df['volatility'].iloc[-1]
            
            # 예측
            result = []
            for i, date in enumerate(prediction_dates):
                day_index = last_day_index + i + 1
                
                # 간단한 예측을 위해 마지막 값 사용
                # 실제로는 이전 예측을 사용하여 이동평균 등을 업데이트해야 함
                features = np.array([[day_index, last_ma_5, last_ma_10, last_ma_20, last_volatility]])
                features_scaled = scaler_X.transform(features)
                
                prediction_scaled = model.predict(features_scaled)
                prediction = scaler_y.inverse_transform(prediction_scaled.reshape(-1, 1)).flatten()[0]
                
                result.append({
                    "date": date.strftime("%Y-%m-%d"),
                    "predicted_price": float(prediction)
                })
            
            return {
                "stock_code": stock_code,
                "model": "LinearRegression",
                "data": result
            }
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"선형 회귀 예측 중 오류 발생: {str(e)}"
        ) 