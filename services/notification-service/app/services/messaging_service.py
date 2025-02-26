"""
메시징 서비스 모듈
"""
import json
import logging
from typing import Any, Dict, Optional

import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractConnection, AbstractChannel

from app.config import settings

logger = logging.getLogger(__name__)


class MessagingService:
    """
    메시징 서비스 클래스
    RabbitMQ를 사용한 메시지 큐 통신을 담당
    """
    
    def __init__(self):
        """
        메시징 서비스 초기화
        """
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None
        self.exchange_name = "notifications"
        self.connection_string = (
            f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@"
            f"{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        )
    
    async def connect(self) -> None:
        """
        RabbitMQ 연결 설정
        """
        if self.connection is None or self.connection.is_closed:
            try:
                # 연결 설정
                self.connection = await connect_robust(self.connection_string)
                
                # 채널 생성
                self.channel = await self.connection.channel()
                
                # 교환기 선언
                await self.channel.declare_exchange(
                    self.exchange_name, aio_pika.ExchangeType.TOPIC, durable=True
                )
                
                logger.info("RabbitMQ 연결 성공")
                
            except Exception as e:
                logger.error(f"RabbitMQ 연결 실패: {str(e)}")
                raise
    
    async def close(self) -> None:
        """
        RabbitMQ 연결 종료
        """
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logger.info("RabbitMQ 연결 종료")
    
    async def publish_message(
        self, routing_key: str, message_data: Dict[str, Any], priority: int = 0
    ) -> None:
        """
        메시지 발행
        
        Args:
            routing_key: 라우팅 키
            message_data: 메시지 데이터
            priority: 메시지 우선순위 (0-9)
        """
        if self.channel is None or self.channel.is_closed:
            await self.connect()
        
        try:
            # 메시지 생성
            message = Message(
                body=json.dumps(message_data).encode(),
                content_type="application/json",
                priority=priority,
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            
            # 메시지 발행
            exchange = await self.channel.get_exchange(self.exchange_name)
            await exchange.publish(message, routing_key=routing_key)
            
            logger.info(f"메시지 발행 성공: {routing_key}")
            
        except Exception as e:
            logger.error(f"메시지 발행 실패: {str(e)}")
            raise
    
    async def subscribe(
        self, routing_key: str, callback, queue_name: Optional[str] = None
    ) -> None:
        """
        메시지 구독
        
        Args:
            routing_key: 라우팅 키
            callback: 메시지 처리 콜백 함수
            queue_name: 큐 이름 (지정하지 않으면 자동 생성)
        """
        if self.channel is None or self.channel.is_closed:
            await self.connect()
        
        try:
            # 큐 선언
            queue = await self.channel.declare_queue(
                queue_name or "", durable=True, auto_delete=queue_name is None
            )
            
            # 라우팅 키로 바인딩
            exchange = await self.channel.get_exchange(self.exchange_name)
            await queue.bind(exchange, routing_key)
            
            # 메시지 소비 시작
            await queue.consume(callback)
            
            logger.info(f"메시지 구독 시작: {routing_key}")
            
        except Exception as e:
            logger.error(f"메시지 구독 실패: {str(e)}")
            raise


# 전역 인스턴스
messaging_service = MessagingService() 