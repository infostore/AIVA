"""
알림 서비스 모듈
"""
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import attributes

from app.models.notification import (
    DeliveryMethod,
    DeliveryStatus,
    Notification,
    NotificationDelivery,
)
from app.schemas.notification import NotificationCreate, NotificationUpdate
from app.services.email_service import email_service


class NotificationService:
    """
    알림 서비스 클래스
    """
    
    async def create_notification(
        self,
        db: AsyncSession,
        notification_in: NotificationCreate,
        creator_id: Optional[str] = None
    ) -> Notification:
        """
        알림 생성
        
        Args:
            db: 데이터베이스 세션
            notification_in: 알림 생성 데이터
            creator_id: 생성자 ID
            
        Returns:
            Notification: 생성된 알림
        """
        # 알림 객체 생성
        notification = Notification(
            user_id=notification_in.user_id,
            type=notification_in.type,
            title=notification_in.title,
            message=notification_in.message,
            data=notification_in.data,
            priority=notification_in.priority,
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        
        # 전송 방법에 따른 알림 전송 처리
        for method in notification_in.delivery_methods:
            # 수신자 정보 가져오기
            recipients = []
            
            if notification_in.recipients and method in notification_in.recipients:
                recipients = notification_in.recipients[method]
            elif notification_in.user_id:
                # 사용자 ID가 있는 경우 해당 사용자의 연락처 정보 가져오기
                # 예: 이메일, 전화번호 등 (여기서는 구현 생략)
                pass
            
            # 전송 정보 생성
            for recipient in recipients:
                delivery = NotificationDelivery(
                    notification_id=notification.id,
                    method=method,
                    status=DeliveryStatus.PENDING,
                    recipient=recipient
                )
                db.add(delivery)
            
            # 이메일 전송 처리
            if method == DeliveryMethod.EMAIL and recipients:
                await self._send_email_notifications(notification, recipients)
        
        await db.commit()
        
        return notification
    
    async def get_notification(
        self,
        db: AsyncSession,
        notification_id: UUID,
        user_id: Optional[UUID] = None
    ) -> Optional[Notification]:
        """
        알림 조회
        
        Args:
            db: 데이터베이스 세션
            notification_id: 알림 ID
            user_id: 사용자 ID (권한 확인용)
            
        Returns:
            Optional[Notification]: 알림 객체 또는 None
        """
        # 알림 조회 쿼리
        query = select(Notification).where(Notification.id == notification_id)
        
        # 사용자 ID가 있는 경우 해당 사용자의 알림만 조회
        if user_id:
            query = query.where(Notification.user_id == user_id)
        
        result = await db.execute(query)
        notification = result.scalar_one_or_none()
        
        return notification
    
    async def update_notification(
        self,
        db: AsyncSession,
        notification_id: UUID,
        notification_in: NotificationUpdate,
        user_id: Optional[UUID] = None
    ) -> Notification:
        """
        알림 업데이트
        
        Args:
            db: 데이터베이스 세션
            notification_id: 알림 ID
            notification_in: 업데이트 데이터
            user_id: 사용자 ID (권한 확인용)
            
        Returns:
            Notification: 업데이트된 알림
        """
        # 알림 조회
        notification = await self.get_notification(db, notification_id, user_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="알림을 찾을 수 없습니다"
            )
        
        # 읽음 상태 업데이트
        if notification_in.is_read is not None and notification_in.is_read != notification.is_read:
            # SQLAlchemy 모델 속성 업데이트를 위해 setattr 사용
            setattr(notification, "is_read", notification_in.is_read)
            
            # 읽음으로 표시한 경우 읽은 시간 업데이트
            if notification_in.is_read:
                setattr(notification, "read_at", datetime.utcnow())
        
        await db.commit()
        await db.refresh(notification)
        
        return notification
    
    async def delete_notification(
        self,
        db: AsyncSession,
        notification_id: UUID,
        user_id: Optional[UUID] = None
    ) -> None:
        """
        알림 삭제
        
        Args:
            db: 데이터베이스 세션
            notification_id: 알림 ID
            user_id: 사용자 ID (권한 확인용)
        """
        # 알림 조회
        notification = await self.get_notification(db, notification_id, user_id)
        
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="알림을 찾을 수 없습니다"
            )
        
        # 알림 삭제
        await db.delete(notification)
        await db.commit()
    
    async def _send_email_notifications(
        self,
        notification: Notification,
        recipients: List[str]
    ) -> None:
        """
        이메일 알림 전송
        
        Args:
            notification: 알림 객체
            recipients: 수신자 이메일 목록
        """
        # SQLAlchemy 모델 속성에서 실제 값 추출
        title = str(getattr(notification, 'title'))
        message = str(getattr(notification, 'message'))
        
        # 이메일 서비스를 통한 이메일 전송
        for recipient in recipients:
            try:
                await email_service.send_email(
                    to_email=recipient,
                    subject=title,
                    html_content=f"<h1>{title}</h1><p>{message}</p>",
                    text_content=f"{title}\n\n{message}"
                )
                
                # 전송 상태 업데이트 (비동기로 처리 가능)
                # await self._update_delivery_status(notification.id, DeliveryMethod.EMAIL, recipient, DeliveryStatus.SENT)
                
            except Exception as e:
                # 오류 로깅 및 상태 업데이트
                # await self._update_delivery_status(notification.id, DeliveryMethod.EMAIL, recipient, DeliveryStatus.FAILED, str(e))
                pass
    
    async def _update_delivery_status(
        self,
        db: AsyncSession,
        notification_id: UUID,
        method: DeliveryMethod,
        recipient: str,
        status: DeliveryStatus,
        error_message: Optional[str] = None
    ) -> None:
        """
        전송 상태 업데이트
        
        Args:
            db: 데이터베이스 세션
            notification_id: 알림 ID
            method: 전송 방법
            recipient: 수신자
            status: 상태
            error_message: 오류 메시지
        """
        # 전송 정보 조회
        query = select(NotificationDelivery).where(
            and_(
                NotificationDelivery.notification_id == notification_id,
                NotificationDelivery.method == method,
                NotificationDelivery.recipient == recipient
            )
        )
        
        result = await db.execute(query)
        delivery = result.scalar_one_or_none()
        
        if delivery:
            # 상태 업데이트 (setattr 사용)
            setattr(delivery, "status", status)
            
            if status == DeliveryStatus.SENT:
                setattr(delivery, "sent_at", datetime.utcnow())
            
            if error_message:
                setattr(delivery, "error_message", error_message)
            
            await db.commit()


# 전역 인스턴스
notification_service = NotificationService() 