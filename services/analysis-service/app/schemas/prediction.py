"""
예측 응답 스키마
"""
from typing import List
from pydantic import BaseModel


class PredictionData(BaseModel):
    """예측 데이터 항목"""
    date: str
    predicted_price: float


class ARIMAPredictionResponse(BaseModel):
    """ARIMA 예측 응답 모델"""
    stock_code: str
    model: str
    data: List[PredictionData]


class LinearRegressionPredictionResponse(BaseModel):
    """선형 회귀 예측 응답 모델"""
    stock_code: str
    model: str
    data: List[PredictionData] 