"""
알림 API 엔드포인트
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.models.notification import NotificationType
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    NotificationUpdate,
)
from app.services.notification_manager import notification_manager

router = APIRouter()


@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    *,
    notification_in: NotificationCreate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    알림 생성
    """
    try:
        # 실제 구현에서는 DB에 저장하고 반환
        # 현재는 임시 구현
        result = await notification_manager.create_and_send_notification(
            title=notification_in.title,
            message=notification_in.message,
            notification_type=notification_in.type.value,
            user_id=notification_in.user_id,
            metadata=notification_in.data,
        )
        
        # 임시 응답 생성
        return {
            "id": result["notification_id"],
            "title": notification_in.title,
            "message": notification_in.message,
            "type": notification_in.type,
            "user_id": notification_in.user_id,
            "data": notification_in.data,
            "created_at": "2023-01-01T00:00:00Z",  # 임시 값
            "is_read": False,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알림 생성 실패: {str(e)}",
        )


@router.get("/", response_model=List[NotificationResponse])
async def read_notifications(
    *,
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[UUID] = None,
    type: Optional[NotificationType] = None,
    is_read: Optional[bool] = None,
) -> Any:
    """
    알림 목록 조회
    """
    # 실제 구현에서는 DB에서 조회
    # 현재는 임시 데이터 반환
    return [
        {
            "id": "123e4567-e89b-12d3-a456-426614174000",
            "title": "테스트 알림",
            "message": "이것은 테스트 알림입니다.",
            "type": NotificationType.INFO,
            "user_id": user_id,
            "data": {"key": "value"},
            "created_at": "2023-01-01T00:00:00Z",
            "is_read": False,
        }
    ]


@router.get("/{notification_id}", response_model=NotificationResponse)
async def read_notification(
    *,
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    알림 상세 조회
    """
    # 실제 구현에서는 DB에서 조회
    # 현재는 임시 데이터 반환
    return {
        "id": notification_id,
        "title": "테스트 알림",
        "message": "이것은 테스트 알림입니다.",
        "type": NotificationType.INFO,
        "user_id": None,
        "data": {"key": "value"},
        "created_at": "2023-01-01T00:00:00Z",
        "is_read": False,
    }


@router.patch("/{notification_id}", response_model=NotificationResponse)
async def update_notification(
    *,
    notification_id: UUID,
    notification_in: NotificationUpdate,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    알림 업데이트 (읽음 상태 등)
    """
    # 실제 구현에서는 DB에서 조회 후 업데이트
    # 현재는 임시 데이터 반환
    return {
        "id": notification_id,
        "title": "테스트 알림",
        "message": "이것은 테스트 알림입니다.",
        "type": NotificationType.INFO,
        "user_id": None,
        "data": notification_in.data or {"key": "value"},
        "created_at": "2023-01-01T00:00:00Z",
        "is_read": notification_in.is_read if notification_in.is_read is not None else False,
    }


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    *,
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
) -> None:
    """
    알림 삭제
    """
    # 실제 구현에서는 DB에서 삭제
    # 현재는 아무 작업도 하지 않음
    pass


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    *,
    notification_id: UUID,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    알림을 읽음으로 표시
    """
    # 실제 구현에서는 DB에서 업데이트
    # 현재는 임시 데이터 반환
    return {
        "id": notification_id,
        "title": "테스트 알림",
        "message": "이것은 테스트 알림입니다.",
        "type": NotificationType.INFO,
        "user_id": None,
        "data": {"key": "value"},
        "created_at": "2023-01-01T00:00:00Z",
        "is_read": True,
    }


@router.post("/send", status_code=status.HTTP_200_OK)
async def send_notification(
    *,
    title: str,
    message: str,
    notification_type: NotificationType = NotificationType.INFO,
    user_id: Optional[UUID] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    device_token: Optional[str] = None,
    channels: List[str] = Query(["email"], description="알림 채널 (email, sms, push)"),
    data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    알림 전송 (직접 호출)
    """
    try:
        result = await notification_manager.create_and_send_notification(
            title=title,
            message=message,
            notification_type=notification_type.value,
            user_id=user_id,
            email=email,
            phone=phone,
            device_token=device_token,
            channels=channels,
            metadata=data,
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"알림 전송 실패: {str(e)}",
        ) 