"""
텍스트 분석 스키마
"""
from datetime import datetime
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class NewsAnalysisRequest(BaseModel):
    """뉴스 분석 요청 스키마"""
    news_ids: List[str] = Field(..., description="분석할 뉴스 ID 목록")
    stock_code: Optional[str] = Field(None, description="관련 종목 코드")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")
    query: Optional[str] = Field(None, description="검색 쿼리")
    max_items: Optional[int] = Field(100, description="최대 분석 항목 수")


class DisclosureAnalysisRequest(BaseModel):
    """공시정보 분석 요청 스키마"""
    disclosure_ids: List[str] = Field(..., description="분석할 공시정보 ID 목록")
    stock_code: Optional[str] = Field(None, description="관련 종목 코드")
    start_date: Optional[datetime] = Field(None, description="시작 날짜")
    end_date: Optional[datetime] = Field(None, description="종료 날짜")
    disclosure_type: Optional[str] = Field(None, description="공시 유형")
    max_items: Optional[int] = Field(100, description="최대 분석 항목 수")


class SentimentAnalysisResult(BaseModel):
    """감성 분석 결과 스키마"""
    positive: float = Field(..., description="긍정적 점수 (0-1)")
    negative: float = Field(..., description="부정적 점수 (0-1)")
    neutral: float = Field(..., description="중립적 점수 (0-1)")
    sentiment: str = Field(..., description="전체 감성 (positive, negative, neutral)")


class EntityAnalysisResult(BaseModel):
    """개체명 분석 결과 스키마"""
    entity: str = Field(..., description="개체명")
    type: str = Field(..., description="개체 유형 (회사, 인물, 제품 등)")
    count: int = Field(..., description="언급 횟수")
    sentiment: Optional[SentimentAnalysisResult] = Field(None, description="개체에 대한 감성 분석")


class KeyphraseAnalysisResult(BaseModel):
    """핵심 문구 분석 결과 스키마"""
    phrase: str = Field(..., description="핵심 문구")
    relevance: float = Field(..., description="관련성 점수 (0-1)")
    count: int = Field(..., description="출현 횟수")


class SummaryAnalysisResult(BaseModel):
    """요약 분석 결과 스키마"""
    summary: str = Field(..., description="텍스트 요약")
    length: int = Field(..., description="요약 길이 (문자)")


class TextAnalysisResponse(BaseModel):
    """텍스트 분석 응답 스키마"""
    request_id: str = Field(..., description="요청 ID")
    analyzed_at: datetime = Field(..., description="분석 시간")
    item_count: int = Field(..., description="분석된 항목 수")
    overall_sentiment: SentimentAnalysisResult = Field(..., description="전체 감성 분석 결과")
    entities: List[EntityAnalysisResult] = Field(..., description="개체명 분석 결과")
    keyphrases: List[KeyphraseAnalysisResult] = Field(..., description="핵심 문구 분석 결과")
    summary: SummaryAnalysisResult = Field(..., description="요약 분석 결과")
    impact_analysis: Dict[str, float] = Field(..., description="주가 영향 분석 (예측)")
    related_topics: List[str] = Field(..., description="관련 주제")


class TextAnalysisError(BaseModel):
    """텍스트 분석 오류 스키마"""
    error_code: str = Field(..., description="오류 코드")
    error_message: str = Field(..., description="오류 메시지")
    request_id: Optional[str] = Field(None, description="요청 ID") 