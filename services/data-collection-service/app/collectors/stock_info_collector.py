"""
주식 기본 정보 수집기
"""
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.models.collection_task import CollectionType

logger = logging.getLogger(__name__)


class StockInfoCollector(BaseCollector):
    """
    주식 기본 정보 수집기
    주식의 기본 정보(회사명, 섹터, 산업 등)를 수집하고 저장
    """
    
    async def collect(self) -> Dict[str, Any]:
        """
        주식 기본 정보 수집
        
        Returns:
            Dict[str, Any]: 수집된 주식 기본 정보
        """
        params = self._parse_parameters()
        
        # 필수 매개변수 확인
        symbol = params.get("symbol")
        if not symbol:
            raise ValueError("주식 심볼이 필요합니다")
        
        logger.info(f"주식 기본 정보 수집 시작: symbol={symbol}")
        
        # 외부 API에서 주식 기본 정보 가져오기
        api_url = f"https://api.example.com/stocks/{symbol}/info"
        response = await self._make_request(api_url)
        
        # 응답 데이터 파싱
        stock_info = response.json()
        
        # 데이터 형식 변환
        formatted_data = {
            "symbol": symbol,
            "company_name": stock_info.get("company_name", ""),
            "exchange": stock_info.get("exchange", ""),
            "currency": stock_info.get("currency", "KRW"),
            "sector": stock_info.get("sector", ""),
            "industry": stock_info.get("industry", ""),
            "market_cap": float(stock_info.get("market_cap", 0)),
            "employees": int(stock_info.get("employees", 0)),
            "website": stock_info.get("website", ""),
            "description": stock_info.get("description", ""),
            "ceo": stock_info.get("ceo", ""),
            "founded_year": stock_info.get("founded_year"),
            "headquarters": stock_info.get("headquarters", ""),
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"주식 기본 정보 수집 완료: symbol={symbol}, company={formatted_data['company_name']}")
        
        return formatted_data
    
    async def store(self, data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        수집된 주식 기본 정보 저장
        
        Args:
            data: 수집된 주식 기본 정보
            
        Returns:
            Tuple[Optional[str], Optional[Dict[str, Any]]]: (저장 위치, 메타데이터)
        """
        if not data:
            logger.warning("저장할 주식 기본 정보가 없습니다")
            return None, None
        
        symbol = data.get("symbol")
        
        # 데이터 저장 로직
        # 예시: 파일 시스템에 JSON 파일로 저장
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"stock_info_{symbol}_{timestamp}.json"
        storage_path = f"data/stock_info/{filename}"
        
        # 실제 구현에서는 파일 시스템이나 클라우드 스토리지에 저장
        # 여기서는 예시로만 로깅
        logger.info(f"주식 기본 정보 저장: path={storage_path}, symbol={symbol}")
        
        # 메타데이터 생성
        metadata = {
            "symbol": symbol,
            "company_name": data.get("company_name", ""),
            "exchange": data.get("exchange", ""),
            "sector": data.get("sector", ""),
            "created_at": datetime.utcnow().isoformat(),
        }
        
        return storage_path, metadata 