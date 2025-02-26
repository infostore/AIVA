from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class MarketType(str, Enum):
    """시장 유형"""
    KOSPI = "KOSPI"
    KOSDAQ = "KOSDAQ"
    NASDAQ = "NASDAQ"
    NYSE = "NYSE"
    AMEX = "AMEX"
    OTHER = "OTHER"


class StockBase(BaseModel):
    """주식 기본 정보"""
    symbol: str = Field(..., description="주식 심볼")
    name: str = Field(..., description="주식 이름")
    market: MarketType = Field(..., description="시장 유형")
    sector: Optional[str] = Field(None, description="섹터")
    industry: Optional[str] = Field(None, description="산업")


class StockPrice(BaseModel):
    """주식 가격 정보"""
    symbol: str = Field(..., description="주식 심볼")
    date: date = Field(..., description="날짜")
    open: float = Field(..., description="시가")
    high: float = Field(..., description="고가")
    low: float = Field(..., description="저가")
    close: float = Field(..., description="종가")
    volume: int = Field(..., description="거래량")
    change: float = Field(..., description="변동률(%)")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")


class TradingTrendType(str, Enum):
    """매매 동향 유형"""
    INDIVIDUAL = "INDIVIDUAL"  # 개인
    FOREIGN = "FOREIGN"        # 외국인
    INSTITUTION = "INSTITUTION"  # 기관
    PENSION = "PENSION"        # 연기금
    FINANCIAL = "FINANCIAL"    # 금융투자
    INSURANCE = "INSURANCE"    # 보험
    TRUST = "TRUST"            # 신탁
    OTHER = "OTHER"            # 기타


class TradingTrend(BaseModel):
    """매매 동향 정보"""
    symbol: str = Field(..., description="주식 심볼")
    date: date = Field(..., description="날짜")
    investor_type: TradingTrendType = Field(..., description="투자자 유형")
    buy_volume: int = Field(..., description="매수 수량")
    sell_volume: int = Field(..., description="매도 수량")
    net_volume: int = Field(..., description="순매수 수량")
    buy_amount: int = Field(..., description="매수 금액")
    sell_amount: int = Field(..., description="매도 금액")
    net_amount: int = Field(..., description="순매수 금액")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")


class QuarterlyRevenueType(str, Enum):
    """분기별 수익 유형"""
    Q1 = "Q1"  # 1분기
    Q2 = "Q2"  # 2분기
    Q3 = "Q3"  # 3분기
    Q4 = "Q4"  # 4분기
    ANNUAL = "ANNUAL"  # 연간


class QuarterlyRevenue(BaseModel):
    """분기별 수익 정보"""
    symbol: str = Field(..., description="주식 심볼")
    year: int = Field(..., description="연도")
    quarter: QuarterlyRevenueType = Field(..., description="분기")
    revenue: float = Field(..., description="매출액")
    operating_profit: float = Field(..., description="영업이익")
    net_profit: float = Field(..., description="순이익")
    eps: float = Field(..., description="주당순이익")
    created_at: datetime = Field(default_factory=datetime.now, description="생성 시간")
    updated_at: datetime = Field(default_factory=datetime.now, description="수정 시간")


class StockWithPrices(StockBase):
    """가격 정보가 포함된 주식 정보"""
    prices: List[StockPrice] = Field(default_factory=list, description="가격 정보 목록")


class StockWithTradingTrends(StockBase):
    """매매 동향 정보가 포함된 주식 정보"""
    trading_trends: List[TradingTrend] = Field(default_factory=list, description="매매 동향 정보 목록")


class StockWithQuarterlyRevenues(StockBase):
    """분기별 수익 정보가 포함된 주식 정보"""
    quarterly_revenues: List[QuarterlyRevenue] = Field(default_factory=list, description="분기별 수익 정보 목록") 