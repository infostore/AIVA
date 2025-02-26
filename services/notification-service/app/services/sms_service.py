"""
SMS 서비스 모듈
"""
import logging
from typing import Dict, List, Optional, Union

from app.config import settings

logger = logging.getLogger(__name__)


class SMSService:
    """
    SMS 서비스 클래스
    문자 메시지 전송을 담당
    """
    
    def __init__(self):
        """
        SMS 서비스 초기화
        """
        # 실제 구현에서는 SMS 서비스 제공업체 설정 추가
        self.api_key = "your-sms-api-key"
        self.sender_phone = "your-sender-phone"
    
    async def send_sms(
        self,
        to_phone: Union[str, List[str]],
        message: str,
        sender: Optional[str] = None,
    ) -> bool:
        """
        SMS 전송
        
        Args:
            to_phone: 수신자 전화번호 (단일 또는 목록)
            message: 메시지 내용
            sender: 발신자 전화번호 (선택 사항)
            
        Returns:
            bool: 전송 성공 여부
        """
        try:
            # 단일 전화번호를 목록으로 변환
            if isinstance(to_phone, str):
                to_phone = [to_phone]
            
            # 발신자 전화번호 설정
            sender = sender or self.sender_phone
            
            # 실제 구현에서는 SMS API 호출
            # 현재는 로깅만 수행
            logger.info(f"SMS 전송: {message[:20]}... -> {len(to_phone)}개 번호")
            
            # SMS API 호출 예시 (실제 구현 시 주석 해제)
            """
            # 예: Twilio API 사용
            from twilio.rest import Client
            
            client = Client(self.account_sid, self.auth_token)
            
            for phone in to_phone:
                message = client.messages.create(
                    body=message,
                    from_=sender,
                    to=phone
                )
                logger.info(f"SMS 전송 완료: {message.sid}")
            """
            
            return True
            
        except Exception as e:
            logger.error(f"SMS 전송 실패: {str(e)}")
            return False
    
    async def send_verification_code(self, phone: str, code: str) -> bool:
        """
        인증 코드 SMS 전송
        
        Args:
            phone: 수신자 전화번호
            code: 인증 코드
            
        Returns:
            bool: 전송 성공 여부
        """
        message = f"[New Data Collector] 인증 코드: {code}\n이 코드는 10분 동안 유효합니다."
        return await self.send_sms(phone, message)
    
    async def send_notification(
        self, phone: str, title: str, message: str
    ) -> bool:
        """
        알림 SMS 전송
        
        Args:
            phone: 수신자 전화번호
            title: 알림 제목
            message: 알림 내용
            
        Returns:
            bool: 전송 성공 여부
        """
        sms_message = f"[{title}] {message}"
        
        # SMS 길이 제한 (일반적으로 160자)
        if len(sms_message) > 160:
            sms_message = sms_message[:157] + "..."
        
        return await self.send_sms(phone, sms_message)


# 전역 인스턴스
sms_service = SMSService() 