"""
주식 데이터 모델 정의
"""
from datetime import date as date_type
from enum import Enum
from typing import Optional, List

from sqlalchemy import ForeignKey, String, Float, Date, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class DataSource(str, Enum):
    """데이터 소스 열거형"""
    YAHOO = "yahoo"
    ALPHA_VANTAGE = "alpha_vantage"
    CUSTOM = "custom"
    KRX = "krx"
    FNGUIDE = "fnguide"


class DataFrequency(str, Enum):
    """데이터 주기 열거형"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    REALTIME = "realtime"
    MINUTE = "minute"


class Stock(Base):
    """주식 정보 모델"""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True, unique=True)
    name: Mapped[str] = mapped_column(String(100), index=True)
    exchange: Mapped[str] = mapped_column(String(50))
    sector: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 관계 정의
    price_data: Mapped[List["StockPrice"]] = relationship(back_populates="stock", cascade="all, delete-orphan")
    financial_data: Mapped[List["FinancialData"]] = relationship(back_populates="stock", cascade="all, delete-orphan")


class StockPrice(Base):
    """주식 가격 데이터 모델"""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock.id", ondelete="CASCADE"))
    date: Mapped[date_type] = mapped_column(Date, index=True)
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    adjusted_close: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    volume: Mapped[int] = mapped_column(Integer)
    source: Mapped[DataSource] = mapped_column(String(20))
    frequency: Mapped[DataFrequency] = mapped_column(String(20))
    
    # 관계 정의
    stock: Mapped["Stock"] = relationship(back_populates="price_data")


class FinancialData(Base):
    """재무 데이터 모델"""
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    stock_id: Mapped[int] = mapped_column(ForeignKey("stock.id", ondelete="CASCADE"))
    period_end_date: Mapped[date_type] = mapped_column(Date, index=True)
    report_date: Mapped[date_type] = mapped_column(Date)
    
    # 재무제표 데이터
    revenue: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    operating_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    net_income: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    eps: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pe_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    pb_ratio: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    dividend_yield: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # 대차대조표 데이터
    total_assets: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_liabilities: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_equity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # 현금흐름표 데이터
    operating_cash_flow: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    investing_cash_flow: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    financing_cash_flow: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    source: Mapped[DataSource] = mapped_column(String(20))
    frequency: Mapped[DataFrequency] = mapped_column(String(20))
    
    # 관계 정의
    stock: Mapped["Stock"] = relationship(back_populates="financial_data") 