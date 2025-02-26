"""
알림 관리자 모듈
여러 알림 채널을 통합 관리
"""
import logging
from typing import Dict, List, Optional, Union, Any
from uuid import UUID

from app.config import settings
from app.models.notification import (
    Notification, NotificationDelivery, DeliveryMethod, 
    DeliveryStatus, NotificationType
)
from app.schemas.notification import NotificationCreate
from app.services.email_service import email_service
from app.services.push_notification_service import PushNotificationService
from app.services.sms_service import sms_service

logger = logging.getLogger(__name__)


class NotificationManager:
    """
    알림 관리자 클래스
    여러 알림 채널(이메일, SMS, 푸시 알림)을 통합 관리
    """
    
    def __init__(self):
        """
        알림 관리자 초기화
        """
        self.push_notification_service = PushNotificationService()
    
    async def send_notification(
        self,
        notification: Notification,
        channels: Optional[List[str]] = None,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        device_token: Optional[str] = None,
    ) -> Dict[str, bool]:
        """
        여러 채널을 통해 알림 전송
        
        Args:
            notification: 알림 객체
            channels: 알림 채널 목록 (email, sms, push)
            user_id: 사용자 ID
            email: 이메일 주소
            phone: 전화번호
            device_token: 기기 토큰
            
        Returns:
            Dict[str, bool]: 각 채널별 전송 결과
        """
        if channels is None:
            channels = ["email"]  # 기본값은 이메일
        
        results = {}
        
        # 알림 내용 준비
        title = str(notification.title)
        message = str(notification.message)
        
        # 각 채널별 전송
        for channel in channels:
            try:
                if channel == "email" and email:
                    success = await email_service.send_email(
                        to_email=email,
                        subject=title,
                        html_content=message,
                    )
                    results["email"] = success
                    
                elif channel == "sms" and phone:
                    success = await sms_service.send_notification(
                        phone=phone,
                        title=title,
                        message=message,
                    )
                    results["sms"] = success
                    
                elif channel == "push" and device_token:
                    success = await self.push_notification_service.send_mobile_push(
                        device_tokens=[device_token],
                        title=title,
                        message=message,
                        data={"notification_id": str(notification.id)},
                    )
                    results["push"] = success
                
                # 전송 결과 기록
                if user_id:
                    delivery = NotificationDelivery(
                        notification_id=notification.id,
                        method=DeliveryMethod(channel),
                        status=DeliveryStatus.SENT if results.get(channel, False) else DeliveryStatus.FAILED,
                        recipient=email if channel == "email" else phone if channel == "sms" else device_token,
                    )
                    # 실제 구현에서는 DB에 저장
                    logger.info(f"알림 전송 기록: {delivery}")
                
            except Exception as e:
                logger.error(f"{channel} 알림 전송 실패: {str(e)}")
                results[channel] = False
        
        return results
    
    async def create_and_send_notification(
        self,
        title: str,
        message: str,
        notification_type: str,
        user_id: Optional[UUID] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        device_token: Optional[str] = None,
        channels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        알림 생성 및 전송
        
        Args:
            title: 알림 제목
            message: 알림 내용
            notification_type: 알림 유형
            user_id: 사용자 ID
            email: 이메일 주소
            phone: 전화번호
            device_token: 기기 토큰
            channels: 알림 채널 목록
            metadata: 추가 메타데이터
            
        Returns:
            Dict: 알림 ID와 전송 결과
        """
        # 알림 유형 변환
        notification_type_enum = NotificationType(notification_type)
        
        # 알림 객체 생성
        notification_data = NotificationCreate(
            title=title,
            message=message,
            type=notification_type_enum,
            user_id=user_id,
            data=metadata or {},
        )
        
        # 실제 구현에서는 DB에 저장하고 ID 반환
        notification = Notification(
            id=1,  # 임시 ID
            title=title,
            message=message,
            type=notification_type_enum,
            user_id=user_id,
            data=metadata or {},
        )
        
        # 알림 전송
        results = await self.send_notification(
            notification=notification,
            channels=channels,
            user_id=user_id,
            email=email,
            phone=phone,
            device_token=device_token,
        )
        
        return {
            "notification_id": notification.id,
            "results": results,
        }


# 전역 인스턴스
notification_manager = NotificationManager() 