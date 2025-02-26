"""
수집 작업 API 테스트
"""
import json
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.models.collection_task import CollectionType, TaskStatus


@pytest.mark.asyncio
async def test_create_collection_task(client: TestClient, db):
    """
    수집 작업 생성 테스트
    """
    # 테스트 데이터
    task_data = {
        "collection_type": CollectionType.STOCK_PRICE,
        "parameters": {
            "symbol": "AAPL",
            "interval": "1d"
        },
        "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        "is_recurring": True,
        "interval_minutes": 60
    }
    
    # API 요청
    response = client.post(
        "/api/v1/collection-tasks/",
        json=task_data
    )
    
    # 응답 검증
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["collection_type"] == CollectionType.STOCK_PRICE
    assert data["status"] == TaskStatus.PENDING
    assert data["is_recurring"] is True
    assert data["interval_minutes"] == 60


@pytest.mark.asyncio
async def test_get_collection_tasks(client: TestClient, db):
    """
    수집 작업 목록 조회 테스트
    """
    # 테스트 데이터 생성 (2개의 작업)
    for i in range(2):
        task_data = {
            "collection_type": CollectionType.STOCK_PRICE if i == 0 else CollectionType.STOCK_INFO,
            "parameters": {
                "symbol": f"TEST{i}",
                "interval": "1d"
            },
            "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
            "is_recurring": i == 0,
            "interval_minutes": 60 if i == 0 else None
        }
        client.post("/api/v1/collection-tasks/", json=task_data)
    
    # API 요청
    response = client.get("/api/v1/collection-tasks/")
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    assert "total" in data
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_get_collection_task(client: TestClient, db):
    """
    수집 작업 상세 조회 테스트
    """
    # 테스트 데이터 생성
    task_data = {
        "collection_type": CollectionType.STOCK_INFO,
        "parameters": {
            "symbol": "GOOG"
        },
        "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        "is_recurring": False
    }
    
    # 작업 생성
    create_response = client.post("/api/v1/collection-tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # API 요청
    response = client.get(f"/api/v1/collection-tasks/{task_id}")
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["collection_type"] == CollectionType.STOCK_INFO
    assert data["status"] == TaskStatus.PENDING
    assert data["is_recurring"] is False


@pytest.mark.asyncio
async def test_update_collection_task(client: TestClient, db):
    """
    수집 작업 업데이트 테스트
    """
    # 테스트 데이터 생성
    task_data = {
        "collection_type": CollectionType.STOCK_PRICE,
        "parameters": {
            "symbol": "MSFT",
            "interval": "1d"
        },
        "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat(),
        "is_recurring": True,
        "interval_minutes": 60
    }
    
    # 작업 생성
    create_response = client.post("/api/v1/collection-tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # 업데이트 데이터
    update_data = {
        "parameters": {
            "symbol": "MSFT",
            "interval": "1h"
        },
        "interval_minutes": 30
    }
    
    # API 요청
    response = client.patch(f"/api/v1/collection-tasks/{task_id}", json=update_data)
    
    # 응답 검증
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == task_id
    assert data["interval_minutes"] == 30
    assert json.loads(data["parameters"])["interval"] == "1h"


@pytest.mark.asyncio
async def test_delete_collection_task(client: TestClient, db):
    """
    수집 작업 삭제 테스트
    """
    # 테스트 데이터 생성
    task_data = {
        "collection_type": CollectionType.STOCK_INFO,
        "parameters": {
            "symbol": "AMZN"
        },
        "scheduled_at": (datetime.utcnow() + timedelta(minutes=5)).isoformat()
    }
    
    # 작업 생성
    create_response = client.post("/api/v1/collection-tasks/", json=task_data)
    task_id = create_response.json()["id"]
    
    # API 요청
    response = client.delete(f"/api/v1/collection-tasks/{task_id}")
    
    # 응답 검증
    assert response.status_code == 204
    
    # 삭제 확인
    get_response = client.get(f"/api/v1/collection-tasks/{task_id}")
    assert get_response.status_code == 404 