"""
기본적 분석 응답 스키마
"""
from typing import List
from pydantic import BaseModel


class PERData(BaseModel):
    """PER 데이터 항목"""
    date: str
    close_price: float
    eps: float
    per: float


class PERResponse(BaseModel):
    """PER 응답 모델"""
    stock_code: str
    data: List[PERData]


class PBRData(BaseModel):
    """PBR 데이터 항목"""
    date: str
    close_price: float
    bps: float
    pbr: float


class PBRResponse(BaseModel):
    """PBR 응답 모델"""
    stock_code: str
    data: List[PBRData]


class ROEData(BaseModel):
    """ROE 데이터 항목"""
    date: str
    net_income: float
    equity: float
    roe: float


class ROEResponse(BaseModel):
    """ROE 응답 모델"""
    stock_code: str
    data: List[ROEData]


class DividendYieldData(BaseModel):
    """배당 수익률 데이터 항목"""
    date: str
    close_price: float
    dividend_per_share: float
    dividend_yield: float


class DividendYieldResponse(BaseModel):
    """배당 수익률 응답 모델"""
    stock_code: str
    data: List[DividendYieldData] 