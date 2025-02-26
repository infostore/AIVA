"""
텍스트 분석 API 엔드포인트
"""
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from langchain.chains import LLMChain
from langchain.chains.summarize import load_summarize_chain
from langchain.llms import LlamaCpp
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

from app.config import settings
from app.schemas.text_analysis import (
    DisclosureAnalysisRequest,
    EntityAnalysisResult,
    KeyphraseAnalysisResult,
    NewsAnalysisRequest,
    SentimentAnalysisResult,
    SummaryAnalysisResult,
    TextAnalysisError,
    TextAnalysisResponse,
)

router = APIRouter()
logger = logging.getLogger(__name__)

# LLM 모델 초기화
llm = LlamaCpp(
    model_path=settings.LLAMA_MODEL_PATH,
    temperature=0,
    max_tokens=2000,
    n_ctx=4096,
    top_p=0.95,
    verbose=False,
)

# 임베딩 모델 초기화
embeddings = HuggingFaceEmbeddings(
    model_name="jhgan/ko-sroberta-multitask",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True},
)

# 텍스트 분할기 초기화
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len,
)

# 프롬프트 템플릿 정의
sentiment_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    다음 텍스트의 감성을 분석해주세요. 긍정적, 부정적, 중립적 점수를 0과 1 사이의 값으로 제공하고, 
    전체적인 감성(positive, negative, neutral)을 결정해주세요.
    
    텍스트: {text}
    
    JSON 형식으로 응답해주세요:
    {{
        "positive": 0.0-1.0 사이의 값,
        "negative": 0.0-1.0 사이의 값,
        "neutral": 0.0-1.0 사이의 값,
        "sentiment": "positive", "negative", "neutral" 중 하나
    }}
    """
)

entity_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    다음 텍스트에서 중요한 개체명(회사, 인물, 제품, 기관 등)을 추출하고 분류해주세요.
    각 개체에 대해 언급 횟수도 계산해주세요.
    
    텍스트: {text}
    
    JSON 형식으로 응답해주세요:
    [
        {{
            "entity": "개체명",
            "type": "개체 유형(회사, 인물, 제품, 기관 등)",
            "count": 언급 횟수
        }},
        ...
    ]
    """
)

keyphrase_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    다음 텍스트에서 핵심 문구를 추출하고, 각 문구의 관련성 점수와 출현 횟수를 계산해주세요.
    
    텍스트: {text}
    
    JSON 형식으로 응답해주세요:
    [
        {{
            "phrase": "핵심 문구",
            "relevance": 0.0-1.0 사이의 관련성 점수,
            "count": 출현 횟수
        }},
        ...
    ]
    """
)

impact_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    다음 텍스트가 주식 시장 또는 특정 주식에 미칠 수 있는 영향을 분석해주세요.
    특히 다음 측면에서 영향을 0.0-1.0 사이의 점수로 평가해주세요:
    - 단기 가격 변동성
    - 장기 투자 가치
    - 거래량 증가 가능성
    - 투자자 심리 영향
    
    텍스트: {text}
    
    JSON 형식으로 응답해주세요:
    {{
        "short_term_price_impact": 0.0-1.0 사이의 값,
        "long_term_value_impact": 0.0-1.0 사이의 값,
        "volume_impact": 0.0-1.0 사이의 값,
        "investor_sentiment_impact": 0.0-1.0 사이의 값
    }}
    """
)

topics_prompt = PromptTemplate(
    input_variables=["text"],
    template="""
    다음 텍스트와 관련된 주요 주제나 키워드를 최대 5개까지 추출해주세요.
    
    텍스트: {text}
    
    JSON 형식으로 응답해주세요:
    ["주제1", "주제2", "주제3", "주제4", "주제5"]
    """
)


async def fetch_news_data(news_ids: List[str]) -> List[Dict[str, Any]]:
    """
    뉴스 데이터를 가져오는 함수
    
    Args:
        news_ids: 뉴스 ID 목록
        
    Returns:
        List[Dict[str, Any]]: 뉴스 데이터 목록
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/news/batch",
                json={"ids": news_ids},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"뉴스 데이터 가져오기 오류: {str(e)}")
        raise HTTPException(status_code=503, detail="뉴스 데이터를 가져올 수 없습니다")


async def fetch_disclosure_data(disclosure_ids: List[str]) -> List[Dict[str, Any]]:
    """
    공시정보 데이터를 가져오는 함수
    
    Args:
        disclosure_ids: 공시정보 ID 목록
        
    Returns:
        List[Dict[str, Any]]: 공시정보 데이터 목록
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.DATA_STORAGE_SERVICE_URL}/api/v1/disclosures/batch",
                json={"ids": disclosure_ids},
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        logger.error(f"공시정보 데이터 가져오기 오류: {str(e)}")
        raise HTTPException(status_code=503, detail="공시정보 데이터를 가져올 수 없습니다")


async def analyze_sentiment(text: str) -> SentimentAnalysisResult:
    """
    텍스트의 감성을 분석하는 함수
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        SentimentAnalysisResult: 감성 분석 결과
    """
    chain = LLMChain(llm=llm, prompt=sentiment_prompt)
    result = await chain.arun(text=text)
    
    try:
        sentiment_data = json.loads(result)
        return SentimentAnalysisResult(
            positive=sentiment_data["positive"],
            negative=sentiment_data["negative"],
            neutral=sentiment_data["neutral"],
            sentiment=sentiment_data["sentiment"],
        )
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"감성 분석 결과 파싱 오류: {str(e)}")
        return SentimentAnalysisResult(
            positive=0.33,
            negative=0.33,
            neutral=0.34,
            sentiment="neutral",
        )


async def extract_entities(text: str) -> List[EntityAnalysisResult]:
    """
    텍스트에서 개체명을 추출하는 함수
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        List[EntityAnalysisResult]: 개체명 분석 결과 목록
    """
    chain = LLMChain(llm=llm, prompt=entity_prompt)
    result = await chain.arun(text=text)
    
    try:
        entities_data = json.loads(result)
        return [
            EntityAnalysisResult(
                entity=entity["entity"],
                type=entity["type"],
                count=entity["count"],
                sentiment=None,
            )
            for entity in entities_data
        ]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"개체명 추출 결과 파싱 오류: {str(e)}")
        return []


async def extract_keyphrases(text: str) -> List[KeyphraseAnalysisResult]:
    """
    텍스트에서 핵심 문구를 추출하는 함수
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        List[KeyphraseAnalysisResult]: 핵심 문구 분석 결과 목록
    """
    chain = LLMChain(llm=llm, prompt=keyphrase_prompt)
    result = await chain.arun(text=text)
    
    try:
        keyphrases_data = json.loads(result)
        return [
            KeyphraseAnalysisResult(
                phrase=keyphrase["phrase"],
                relevance=keyphrase["relevance"],
                count=keyphrase["count"],
            )
            for keyphrase in keyphrases_data
        ]
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"핵심 문구 추출 결과 파싱 오류: {str(e)}")
        return []


async def analyze_impact(text: str) -> Dict[str, float]:
    """
    텍스트가 주식 시장에 미칠 영향을 분석하는 함수
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        Dict[str, float]: 영향 분석 결과
    """
    chain = LLMChain(llm=llm, prompt=impact_prompt)
    result = await chain.arun(text=text)
    
    try:
        impact_data = json.loads(result)
        return impact_data
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"영향 분석 결과 파싱 오류: {str(e)}")
        return {
            "short_term_price_impact": 0.5,
            "long_term_value_impact": 0.5,
            "volume_impact": 0.5,
            "investor_sentiment_impact": 0.5,
        }


async def extract_topics(text: str) -> List[str]:
    """
    텍스트에서 관련 주제를 추출하는 함수
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        List[str]: 관련 주제 목록
    """
    chain = LLMChain(llm=llm, prompt=topics_prompt)
    result = await chain.arun(text=text)
    
    try:
        topics_data = json.loads(result)
        return topics_data
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"주제 추출 결과 파싱 오류: {str(e)}")
        return []


async def generate_summary(texts: List[str]) -> SummaryAnalysisResult:
    """
    텍스트 목록에서 요약을 생성하는 함수
    
    Args:
        texts: 요약할 텍스트 목록
        
    Returns:
        SummaryAnalysisResult: 요약 분석 결과
    """
    # 텍스트 결합 및 분할
    combined_text = " ".join(texts)
    docs = [Document(page_content=combined_text)]
    
    # 요약 체인 생성
    chain = load_summarize_chain(
        llm=llm,
        chain_type="map_reduce",
        verbose=False,
    )
    
    # 요약 생성
    summary = await chain.arun(docs)
    
    return SummaryAnalysisResult(
        summary=summary,
        length=len(summary),
    )


@router.post("/news", response_model=TextAnalysisResponse)
async def analyze_news(request: NewsAnalysisRequest) -> TextAnalysisResponse:
    """
    뉴스 분석 API 엔드포인트
    
    Args:
        request: 뉴스 분석 요청
        
    Returns:
        TextAnalysisResponse: 텍스트 분석 응답
    """
    try:
        # 뉴스 데이터 가져오기
        news_data = await fetch_news_data(request.news_ids)
        
        if not news_data:
            raise HTTPException(status_code=404, detail="뉴스 데이터를 찾을 수 없습니다")
        
        # 분석할 텍스트 추출
        texts = [f"제목: {news['title']}\n내용: {news['content']}" for news in news_data]
        combined_text = "\n\n".join(texts)
        
        # 병렬로 분석 작업 수행
        sentiment_result = await analyze_sentiment(combined_text)
        entities_result = await extract_entities(combined_text)
        keyphrases_result = await extract_keyphrases(combined_text)
        impact_result = await analyze_impact(combined_text)
        topics_result = await extract_topics(combined_text)
        summary_result = await generate_summary(texts)
        
        # 응답 생성
        return TextAnalysisResponse(
            request_id=str(uuid.uuid4()),
            analyzed_at=datetime.now(),
            item_count=len(news_data),
            overall_sentiment=sentiment_result,
            entities=entities_result,
            keyphrases=keyphrases_result,
            summary=summary_result,
            impact_analysis=impact_result,
            related_topics=topics_result,
        )
        
    except Exception as e:
        logger.error(f"뉴스 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"뉴스 분석 중 오류가 발생했습니다: {str(e)}")


@router.post("/disclosure", response_model=TextAnalysisResponse)
async def analyze_disclosure(request: DisclosureAnalysisRequest) -> TextAnalysisResponse:
    """
    공시정보 분석 API 엔드포인트
    
    Args:
        request: 공시정보 분석 요청
        
    Returns:
        TextAnalysisResponse: 텍스트 분석 응답
    """
    try:
        # 공시정보 데이터 가져오기
        disclosure_data = await fetch_disclosure_data(request.disclosure_ids)
        
        if not disclosure_data:
            raise HTTPException(status_code=404, detail="공시정보 데이터를 찾을 수 없습니다")
        
        # 분석할 텍스트 추출
        texts = [f"제목: {disc['title']}\n내용: {disc.get('content', '내용 없음')}" for disc in disclosure_data]
        combined_text = "\n\n".join(texts)
        
        # 병렬로 분석 작업 수행
        sentiment_result = await analyze_sentiment(combined_text)
        entities_result = await extract_entities(combined_text)
        keyphrases_result = await extract_keyphrases(combined_text)
        impact_result = await analyze_impact(combined_text)
        topics_result = await extract_topics(combined_text)
        summary_result = await generate_summary(texts)
        
        # 응답 생성
        return TextAnalysisResponse(
            request_id=str(uuid.uuid4()),
            analyzed_at=datetime.now(),
            item_count=len(disclosure_data),
            overall_sentiment=sentiment_result,
            entities=entities_result,
            keyphrases=keyphrases_result,
            summary=summary_result,
            impact_analysis=impact_result,
            related_topics=topics_result,
        )
        
    except Exception as e:
        logger.error(f"공시정보 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"공시정보 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/sentiment", response_model=SentimentAnalysisResult)
async def analyze_text_sentiment(text: str = Query(..., min_length=10)) -> SentimentAnalysisResult:
    """
    텍스트 감성 분석 API 엔드포인트
    
    Args:
        text: 분석할 텍스트
        
    Returns:
        SentimentAnalysisResult: 감성 분석 결과
    """
    try:
        return await analyze_sentiment(text)
    except Exception as e:
        logger.error(f"텍스트 감성 분석 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"텍스트 감성 분석 중 오류가 발생했습니다: {str(e)}")


@router.get("/summary", response_model=SummaryAnalysisResult)
async def summarize_text(text: str = Query(..., min_length=100)) -> SummaryAnalysisResult:
    """
    텍스트 요약 API 엔드포인트
    
    Args:
        text: 요약할 텍스트
        
    Returns:
        SummaryAnalysisResult: 요약 분석 결과
    """
    try:
        return await generate_summary([text])
    except Exception as e:
        logger.error(f"텍스트 요약 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"텍스트 요약 중 오류가 발생했습니다: {str(e)}") 