"""
알림 모델
"""
import enum
from datetime import datetime
from typing import Dict, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class NotificationType(str, enum.Enum):
    """
    알림 유형 열거형
    """
    SYSTEM = "system"  # 시스템 알림
    TASK = "task"      # 작업 관련 알림
    ERROR = "error"    # 오류 알림
    INFO = "info"      # 정보 알림
    WARNING = "warning"  # 경고 알림


class NotificationPriority(str, enum.Enum):
    """
    알림 우선순위 열거형
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class DeliveryStatus(str, enum.Enum):
    """
    전송 상태 열거형
    """
    PENDING = "pending"  # 대기 중
    SENT = "sent"        # 전송됨
    FAILED = "failed"    # 실패
    READ = "read"        # 읽음


class Notification(Base):
    """
    알림 모델
    """
    __tablename__ = "notifications"
    
    id = Column(PGUUID, primary_key=True, default=uuid4)
    user_id = Column(PGUUID, nullable=True, index=True)  # 수신자 ID (없으면 전체 알림)
    type = Column(Enum(NotificationType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSONB, nullable=True)  # 추가 데이터 (JSON)
    priority = Column(Enum(NotificationPriority), default=NotificationPriority.MEDIUM)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime, nullable=True)
    
    # 전송 관련 정보
    deliveries = relationship("NotificationDelivery", back_populates="notification", cascade="all, delete-orphan")
    
    # 인덱스
    __table_args__ = (
        Index("ix_notifications_created_at", created_at.desc()),
        Index("ix_notifications_user_id_type", user_id, type),
    )
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, type={self.type}, title={self.title})>"
    
    def to_dict(self) -> Dict:
        """
        알림을 딕셔너리로 변환
        
        Returns:
            Dict: 알림 딕셔너리
        """
        return {
            "id": str(self.id),
            "user_id": str(self.user_id) if self.user_id else None,
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
            "read_at": self.read_at.isoformat() if self.read_at else None
        }


class DeliveryMethod(str, enum.Enum):
    """
    전송 방법 열거형
    """
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"
    WEB = "web"


class NotificationDelivery(Base):
    """
    알림 전송 모델
    """
    __tablename__ = "notification_deliveries"
    
    id = Column(PGUUID, primary_key=True, default=uuid4)
    notification_id = Column(PGUUID, ForeignKey("notifications.id", ondelete="CASCADE"), nullable=False)
    method = Column(Enum(DeliveryMethod), nullable=False)
    status = Column(Enum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False)
    recipient = Column(String(255), nullable=True)  # 이메일 주소, 전화번호 등
    sent_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # 관계
    notification = relationship("Notification", back_populates="deliveries")
    
    # 인덱스
    __table_args__ = (
        Index("ix_notification_deliveries_notification_id", notification_id),
        Index("ix_notification_deliveries_status", status),
    )
    
    def __repr__(self) -> str:
        return f"<NotificationDelivery(id={self.id}, method={self.method}, status={self.status})>"
    
    def to_dict(self) -> Dict:
        """
        전송 정보를 딕셔너리로 변환
        
        Returns:
            Dict: 전송 정보 딕셔너리
        """
        return {
            "id": str(self.id),
            "notification_id": str(self.notification_id),
            "method": self.method,
            "status": self.status,
            "recipient": self.recipient,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "error_message": self.error_message
        } 