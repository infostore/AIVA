"""
기술적 분석 응답 스키마
"""
from typing import List
from pydantic import BaseModel


class MovingAverageData(BaseModel):
    """이동평균 데이터 항목"""
    date: str
    close_price: float
    ma_value: float


class MovingAverageResponse(BaseModel):
    """이동평균 응답 모델"""
    stock_code: str
    period: int
    data: List[MovingAverageData]


class RSIData(BaseModel):
    """RSI 데이터 항목"""
    date: str
    close_price: float
    rsi_value: float


class RSIResponse(BaseModel):
    """RSI 응답 모델"""
    stock_code: str
    period: int
    data: List[RSIData]


class MACDData(BaseModel):
    """MACD 데이터 항목"""
    date: str
    close_price: float
    macd_line: float
    signal_line: float
    histogram: float


class MACDResponse(BaseModel):
    """MACD 응답 모델"""
    stock_code: str
    fast_period: int
    slow_period: int
    signal_period: int
    data: List[MACDData]


class BollingerBandsData(BaseModel):
    """볼린저 밴드 데이터 항목"""
    date: str
    close_price: float
    upper_band: float
    middle_band: float
    lower_band: float


class BollingerBandsResponse(BaseModel):
    """볼린저 밴드 응답 모델"""
    stock_code: str
    period: int
    std_dev: float
    data: List[BollingerBandsData] 