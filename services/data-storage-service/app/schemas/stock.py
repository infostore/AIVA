"""
주식 데이터 스키마 정의
"""
from datetime import date as date_type
from typing import List, Optional, Annotated

from pydantic import BaseModel, Field, ConfigDict

from app.models.stock_data import DataSource, DataFrequency


# 주식 스키마
class StockBase(BaseModel):
    """주식 기본 스키마"""
    symbol: Annotated[str, Field(description="주식 심볼", examples=["AAPL"])]
    name: Annotated[str, Field(description="주식 이름", examples=["Apple Inc."])]
    exchange: Annotated[str, Field(description="거래소", examples=["NASDAQ"])]
    sector: Annotated[Optional[str], Field(description="섹터", examples=["Technology"])] = None
    industry: Annotated[Optional[str], Field(description="산업", examples=["Consumer Electronics"])] = None
    country: Annotated[str, Field(description="국가", examples=["USA"])]
    description: Annotated[Optional[str], Field(description="설명")] = None


class StockCreate(StockBase):
    """주식 생성 스키마"""
    pass


class StockUpdate(BaseModel):
    """주식 업데이트 스키마"""
    name: Annotated[Optional[str], Field(description="주식 이름")] = None
    exchange: Annotated[Optional[str], Field(description="거래소")] = None
    sector: Annotated[Optional[str], Field(description="섹터")] = None
    industry: Annotated[Optional[str], Field(description="산업")] = None
    country: Annotated[Optional[str], Field(description="국가")] = None
    description: Annotated[Optional[str], Field(description="설명")] = None


# 주식 가격 스키마
class StockPriceBase(BaseModel):
    """주식 가격 기본 스키마"""
    date: Annotated[date_type, Field(description="날짜")]
    open: Annotated[float, Field(description="시가")]
    high: Annotated[float, Field(description="고가")]
    low: Annotated[float, Field(description="저가")]
    close: Annotated[float, Field(description="종가")]
    adjusted_close: Annotated[Optional[float], Field(description="수정 종가")] = None
    volume: Annotated[int, Field(description="거래량")]
    source: Annotated[DataSource, Field(description="데이터 소스")]
    frequency: Annotated[DataFrequency, Field(description="데이터 주기")]


class StockPriceCreate(StockPriceBase):
    """주식 가격 생성 스키마"""
    stock_id: Annotated[int, Field(description="주식 ID")]


class StockPriceUpdate(BaseModel):
    """주식 가격 업데이트 스키마"""
    open: Annotated[Optional[float], Field(description="시가")] = None
    high: Annotated[Optional[float], Field(description="고가")] = None
    low: Annotated[Optional[float], Field(description="저가")] = None
    close: Annotated[Optional[float], Field(description="종가")] = None
    adjusted_close: Annotated[Optional[float], Field(description="수정 종가")] = None
    volume: Annotated[Optional[int], Field(description="거래량")] = None
    source: Annotated[Optional[DataSource], Field(description="데이터 소스")] = None
    frequency: Annotated[Optional[DataFrequency], Field(description="데이터 주기")] = None


# 재무 데이터 스키마
class FinancialDataBase(BaseModel):
    """재무 데이터 기본 스키마"""
    period_end_date: Annotated[date_type, Field(description="기간 종료일")]
    report_date: Annotated[date_type, Field(description="보고일")]
    revenue: Annotated[Optional[float], Field(description="매출")] = None
    operating_income: Annotated[Optional[float], Field(description="영업이익")] = None
    net_income: Annotated[Optional[float], Field(description="순이익")] = None
    eps: Annotated[Optional[float], Field(description="주당순이익")] = None
    pe_ratio: Annotated[Optional[float], Field(description="주가수익비율")] = None
    pb_ratio: Annotated[Optional[float], Field(description="주가순자산비율")] = None
    dividend_yield: Annotated[Optional[float], Field(description="배당수익률")] = None
    total_assets: Annotated[Optional[float], Field(description="총자산")] = None
    total_liabilities: Annotated[Optional[float], Field(description="총부채")] = None
    total_equity: Annotated[Optional[float], Field(description="총자본")] = None
    operating_cash_flow: Annotated[Optional[float], Field(description="영업현금흐름")] = None
    investing_cash_flow: Annotated[Optional[float], Field(description="투자현금흐름")] = None
    financing_cash_flow: Annotated[Optional[float], Field(description="재무현금흐름")] = None
    source: Annotated[DataSource, Field(description="데이터 소스")]
    frequency: Annotated[DataFrequency, Field(description="데이터 주기")]


class FinancialDataCreate(FinancialDataBase):
    """재무 데이터 생성 스키마"""
    stock_id: Annotated[int, Field(description="주식 ID")]


class FinancialDataUpdate(BaseModel):
    """재무 데이터 업데이트 스키마"""
    report_date: Annotated[Optional[date_type], Field(description="보고일")] = None
    revenue: Annotated[Optional[float], Field(description="매출")] = None
    operating_income: Annotated[Optional[float], Field(description="영업이익")] = None
    net_income: Annotated[Optional[float], Field(description="순이익")] = None
    eps: Annotated[Optional[float], Field(description="주당순이익")] = None
    pe_ratio: Annotated[Optional[float], Field(description="주가수익비율")] = None
    pb_ratio: Annotated[Optional[float], Field(description="주가순자산비율")] = None
    dividend_yield: Annotated[Optional[float], Field(description="배당수익률")] = None
    total_assets: Annotated[Optional[float], Field(description="총자산")] = None
    total_liabilities: Annotated[Optional[float], Field(description="총부채")] = None
    total_equity: Annotated[Optional[float], Field(description="총자본")] = None
    operating_cash_flow: Annotated[Optional[float], Field(description="영업현금흐름")] = None
    investing_cash_flow: Annotated[Optional[float], Field(description="투자현금흐름")] = None
    financing_cash_flow: Annotated[Optional[float], Field(description="재무현금흐름")] = None
    source: Annotated[Optional[DataSource], Field(description="데이터 소스")] = None
    frequency: Annotated[Optional[DataFrequency], Field(description="데이터 주기")] = None


# 응답 스키마
class StockPrice(StockPriceBase):
    """주식 가격 응답 스키마"""
    id: int
    stock_id: int
    
    model_config = ConfigDict(from_attributes=True)


class FinancialData(FinancialDataBase):
    """재무 데이터 응답 스키마"""
    id: int
    stock_id: int
    
    model_config = ConfigDict(from_attributes=True)


class Stock(StockBase):
    """주식 응답 스키마"""
    id: int
    price_data: List[StockPrice] = []
    financial_data: List[FinancialData] = []
    
    model_config = ConfigDict(from_attributes=True)


class StockWithoutData(StockBase):
    """데이터 없는 주식 응답 스키마"""
    id: int
    
    model_config = ConfigDict(from_attributes=True) 