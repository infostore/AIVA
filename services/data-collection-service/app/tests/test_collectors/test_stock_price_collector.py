"""
주식 가격 수집기 테스트
"""
import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import Response

from app.collectors.stock_price_collector import StockPriceCollector
from app.utils.date_utils import format_date


@pytest.fixture
def mock_response_data():
    """
    모의 응답 데이터 생성
    """
    today = datetime.utcnow()
    yesterday = today - timedelta(days=1)
    two_days_ago = today - timedelta(days=2)
    
    return {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "prices": [
            {
                "date": format_date(two_days_ago),
                "open": 150.0,
                "high": 152.5,
                "low": 149.5,
                "close": 151.0,
                "volume": 1000000
            },
            {
                "date": format_date(yesterday),
                "open": 151.0,
                "high": 153.0,
                "low": 150.0,
                "close": 152.0,
                "volume": 1100000
            },
            {
                "date": format_date(today),
                "open": 152.0,
                "high": 155.0,
                "low": 151.5,
                "close": 154.0,
                "volume": 1200000
            }
        ]
    }


@pytest.mark.asyncio
async def test_collect_stock_price_data(mock_response_data):
    """
    주식 가격 데이터 수집 테스트
    """
    # 모의 HTTP 클라이언트 설정
    mock_response = Response(
        status_code=200,
        json=mock_response_data,
        content=json.dumps(mock_response_data).encode()
    )
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    # 모의 데이터 스토리지 서비스 설정
    mock_storage_service = AsyncMock()
    mock_storage_service.store_stock_price_data.return_value = {"status": "success"}
    
    # 테스트 매개변수
    parameters = {
        "symbol": "AAPL",
        "interval": "1d",
        "start_date": format_date(datetime.utcnow() - timedelta(days=7)),
        "end_date": format_date(datetime.utcnow())
    }
    
    # 패치 적용
    with patch("httpx.AsyncClient", return_value=mock_client), \
         patch("app.services.data_storage_service.data_storage_service", mock_storage_service):
        
        # 수집기 생성 및 실행
        collector = StockPriceCollector(parameters)
        result = await collector.collect()
        
        # 검증
        assert result is not None
        assert "symbol" in result
        assert result["symbol"] == "AAPL"
        assert "data_points" in result
        assert result["data_points"] == 3
        
        # API 호출 검증
        mock_client.get.assert_called_once()
        
        # 데이터 저장 검증
        mock_storage_service.store_stock_price_data.assert_called_once_with(
            "AAPL", "1d", mock_response_data["prices"]
        )


@pytest.mark.asyncio
async def test_collect_stock_price_data_error():
    """
    주식 가격 데이터 수집 오류 테스트
    """
    # 모의 HTTP 클라이언트 설정 (오류 응답)
    mock_response = Response(
        status_code=404,
        json={"error": "Symbol not found"},
        content=json.dumps({"error": "Symbol not found"}).encode()
    )
    
    mock_client = AsyncMock()
    mock_client.get.return_value = mock_response
    
    # 테스트 매개변수
    parameters = {
        "symbol": "INVALID",
        "interval": "1d"
    }
    
    # 패치 적용
    with patch("httpx.AsyncClient", return_value=mock_client), \
         pytest.raises(Exception) as excinfo:
        
        # 수집기 생성 및 실행
        collector = StockPriceCollector(parameters)
        await collector.collect()
    
    # 오류 메시지 검증
    assert "Symbol not found" in str(excinfo.value) 