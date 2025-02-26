"""
알림 스키마
"""
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.notification import NotificationType, NotificationPriority, DeliveryStatus, DeliveryMethod


class NotificationBase(BaseModel):
    """
    알림 기본 스키마
    """
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")
    type: NotificationType = Field(default=NotificationType.INFO, description="알림 유형")
    priority: NotificationPriority = Field(default=NotificationPriority.MEDIUM, description="알림 우선순위")
    data: Optional[Dict[str, Any]] = Field(default=None, description="추가 데이터")


class NotificationCreate(NotificationBase):
    """
    알림 생성 스키마
    """
    user_id: Optional[UUID] = Field(default=None, description="사용자 ID")


class NotificationUpdate(BaseModel):
    """
    알림 업데이트 스키마
    """
    title: Optional[str] = Field(default=None, description="알림 제목")
    message: Optional[str] = Field(default=None, description="알림 내용")
    type: Optional[NotificationType] = Field(default=None, description="알림 유형")
    priority: Optional[NotificationPriority] = Field(default=None, description="알림 우선순위")
    data: Optional[Dict[str, Any]] = Field(default=None, description="추가 데이터")
    is_read: Optional[bool] = Field(default=None, description="읽음 여부")


class NotificationResponse(NotificationBase):
    """
    알림 응답 스키마
    """
    id: UUID = Field(..., description="알림 ID")
    user_id: Optional[UUID] = Field(default=None, description="사용자 ID")
    created_at: datetime = Field(..., description="생성 시간")
    is_read: bool = Field(default=False, description="읽음 여부")
    read_at: Optional[datetime] = Field(default=None, description="읽은 시간")

    class Config:
        from_attributes = True


class NotificationDeliveryBase(BaseModel):
    """
    알림 전송 기본 스키마
    """
    method: DeliveryMethod = Field(..., description="전송 방법")
    recipient: Optional[str] = Field(default=None, description="수신자 정보 (이메일, 전화번호 등)")


class NotificationDeliveryCreate(NotificationDeliveryBase):
    """
    알림 전송 생성 스키마
    """
    notification_id: UUID = Field(..., description="알림 ID")


class NotificationDeliveryUpdate(BaseModel):
    """
    알림 전송 업데이트 스키마
    """
    status: Optional[DeliveryStatus] = Field(default=None, description="전송 상태")
    error_message: Optional[str] = Field(default=None, description="오류 메시지")


class NotificationDeliveryResponse(NotificationDeliveryBase):
    """
    알림 전송 응답 스키마
    """
    id: UUID = Field(..., description="전송 ID")
    notification_id: UUID = Field(..., description="알림 ID")
    status: DeliveryStatus = Field(..., description="전송 상태")
    sent_at: Optional[datetime] = Field(default=None, description="전송 시간")
    error_message: Optional[str] = Field(default=None, description="오류 메시지")

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """
    알림 목록 응답 스키마
    """
    items: List[NotificationResponse] = Field(..., description="알림 목록")
    total: int = Field(..., description="총 개수")


class NotificationSendRequest(BaseModel):
    """
    알림 전송 요청 스키마
    """
    title: str = Field(..., description="알림 제목")
    message: str = Field(..., description="알림 내용")
    type: NotificationType = Field(default=NotificationType.INFO, description="알림 유형")
    user_id: Optional[UUID] = Field(default=None, description="사용자 ID")
    email: Optional[str] = Field(default=None, description="이메일 주소")
    phone: Optional[str] = Field(default=None, description="전화번호")
    device_token: Optional[str] = Field(default=None, description="기기 토큰")
    channels: List[str] = Field(default=["email"], description="알림 채널 (email, sms, push)")
    data: Optional[Dict[str, Any]] = Field(default=None, description="추가 데이터")