"""
데이터 스토리지 서비스 연동 모듈
"""
import logging
from typing import Any, Dict, List, Optional

import httpx
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)


class DataStorageService:
    """
    데이터 스토리지 서비스 클라이언트
    """
    
    def __init__(self):
        """
        클라이언트 초기화
        """
        self.base_url = settings.DATA_STORAGE_SERVICE_URL
        self.timeout = 30.0  # 요청 타임아웃 (초)
    
    async def store_stock_price_data(
        self, symbol: str, interval: str, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        주식 가격 데이터 저장
        
        Args:
            symbol: 주식 심볼
            interval: 데이터 간격 (1d, 1h 등)
            data: 저장할 데이터 목록
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = f"/stock-prices/{symbol}"
        payload = {
            "symbol": symbol,
            "interval": interval,
            "data": data
        }
        
        return await self._post(endpoint, payload)
    
    async def store_stock_info(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        주식 정보 저장
        
        Args:
            symbol: 주식 심볼
            data: 저장할 데이터
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = f"/stock-info/{symbol}"
        return await self._post(endpoint, data)
    
    async def store_market_index(
        self, index_code: str, interval: str, data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        시장 지수 데이터 저장
        
        Args:
            index_code: 지수 코드
            interval: 데이터 간격
            data: 저장할 데이터 목록
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = f"/market-indices/{index_code}"
        payload = {
            "index_code": index_code,
            "interval": interval,
            "data": data
        }
        
        return await self._post(endpoint, payload)
    
    async def store_news_data(self, news_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        뉴스 데이터 저장
        
        Args:
            news_data: 저장할 뉴스 데이터 목록
            
        Returns:
            Dict[str, Any]: 응답 데이터
        """
        endpoint = "/news"
        return await self._post(endpoint, {"news": news_data})
    
    async def _post(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST 요청 전송
        
        Args:
            endpoint: API 엔드포인트
            data: 요청 데이터
            
        Returns:
            Dict[str, Any]: 응답 데이터
            
        Raises:
            HTTPException: API 요청 실패 시
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=data)
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPStatusError as e:
            logger.error(f"API 오류 응답: {e.response.status_code} - {e.response.text}")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"데이터 스토리지 서비스 오류: {e.response.text}"
            )
            
        except httpx.RequestError as e:
            logger.error(f"API 요청 실패: {str(e)}")
            raise HTTPException(
                status_code=503,
                detail=f"데이터 스토리지 서비스 연결 실패: {str(e)}"
            )


# 전역 인스턴스
data_storage_service = DataStorageService() 