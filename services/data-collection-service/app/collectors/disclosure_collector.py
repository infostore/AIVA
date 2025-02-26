"""
공시정보 수집기
한국거래소(KRX)와 금융감독원(FSS)의 DART 시스템에서 공시정보를 수집
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import httpx
from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.models.collection_task import CollectionResult, CollectionTask

logger = logging.getLogger(__name__)


class DisclosureCollector(BaseCollector):
    """
    공시정보 수집기 클래스
    한국거래소(KRX)와 금융감독원(FSS)의 DART 시스템에서 공시정보를 수집
    """
    
    def __init__(self, db: Session, task: CollectionTask):
        """
        초기화
        
        Args:
            db: 데이터베이스 세션
            task: 수집 작업 객체
        """
        super().__init__(db, task)
        self.params = self._parse_parameters()
        self.api_key = self.params.get("api_key", "")
        self.source = self.params.get("source", "dart")  # 'dart' 또는 'krx'
        self.start_date = self.params.get("start_date", (datetime.now() - timedelta(days=7)).strftime("%Y%m%d"))
        self.end_date = self.params.get("end_date", datetime.now().strftime("%Y%m%d"))
        self.corp_code = self.params.get("corp_code", "")  # 특정 회사 코드 (선택적)
        self.disclosure_type = self.params.get("disclosure_type", "")  # 공시 유형 (선택적)
    
    async def collect(self) -> List[Dict[str, Any]]:
        """
        공시정보 수집 로직 구현
        
        Returns:
            List[Dict[str, Any]]: 수집된 공시정보 목록
        """
        logger.info(f"공시정보 수집 시작: source={self.source}, start_date={self.start_date}, end_date={self.end_date}")
        
        if self.source.lower() == "dart":
            return await self._collect_from_dart()
        elif self.source.lower() == "krx":
            return await self._collect_from_krx()
        else:
            raise ValueError(f"지원되지 않는 공시정보 소스: {self.source}")
    
    async def _collect_from_dart(self) -> List[Dict[str, Any]]:
        """
        금융감독원 DART 시스템에서 공시정보 수집
        
        Returns:
            List[Dict[str, Any]]: 수집된 공시정보 목록
        """
        if not self.api_key:
            raise ValueError("DART API 키가 필요합니다")
        
        # DART Open API 엔드포인트
        url = "https://opendart.fss.or.kr/api/list.json"
        
        # 요청 파라미터 구성
        params = {
            "crtfc_key": self.api_key,
            "bgn_de": self.start_date,
            "end_de": self.end_date,
            "page_count": 100,  # 한 페이지당 최대 항목 수
        }
        
        # 특정 회사 코드가 있는 경우 추가
        if self.corp_code:
            params["corp_code"] = self.corp_code
            
        # 공시 유형이 있는 경우 추가
        if self.disclosure_type:
            params["pblntf_ty"] = self.disclosure_type
        
        # API 요청
        response = await self._make_request(url, params=params)
        data = response.json()
        
        if data.get("status") != "000":
            error_message = data.get("message", "알 수 없는 오류")
            logger.error(f"DART API 오류: {error_message}")
            raise Exception(f"DART API 오류: {error_message}")
        
        disclosures = data.get("list", [])
        logger.info(f"DART에서 {len(disclosures)}개의 공시정보 수집 완료")
        
        # 필요한 필드 추출 및 변환
        processed_disclosures = []
        for disclosure in disclosures:
            processed_disclosure = {
                "source": "dart",
                "corp_code": disclosure.get("corp_code"),
                "corp_name": disclosure.get("corp_name"),
                "stock_code": disclosure.get("stock_code"),
                "disclosure_id": disclosure.get("rcept_no"),
                "title": disclosure.get("report_nm"),
                "disclosure_type": disclosure.get("pblntf_ty"),
                "disclosure_date": disclosure.get("rcept_dt"),
                "url": f"https://dart.fss.or.kr/dsaf001/main.do?rcpNo={disclosure.get('rcept_no')}",
                "submitted_at": datetime.now().isoformat(),
                "raw_data": disclosure
            }
            processed_disclosures.append(processed_disclosure)
        
        return processed_disclosures
    
    async def _collect_from_krx(self) -> List[Dict[str, Any]]:
        """
        한국거래소(KRX)에서 공시정보 수집
        
        Returns:
            List[Dict[str, Any]]: 수집된 공시정보 목록
        """
        # KRX 공시정보 API 엔드포인트
        url = "http://data.krx.co.kr/comm/bldAttendant/getJsonData.cmd"
        
        # 요청 헤더
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        # 요청 파라미터 구성
        params = {
            "bld": "dbms/MDC/STAT/standard/MDCSTAT03701",
            "locale": "ko_KR",
            "mktId": "ALL",  # 전체 시장
            "strtDd": self.start_date,
            "endDd": self.end_date,
            "share": "1",
            "csvxls_isNo": "false"
        }
        
        # API 요청
        response = await self._make_request(url, method="POST", headers=headers, data=params)
        data = response.json()
        
        disclosures = data.get("OutBlock_1", [])
        logger.info(f"KRX에서 {len(disclosures)}개의 공시정보 수집 완료")
        
        # 필요한 필드 추출 및 변환
        processed_disclosures = []
        for disclosure in disclosures:
            processed_disclosure = {
                "source": "krx",
                "corp_name": disclosure.get("korSecnNm"),
                "stock_code": disclosure.get("shotnIsin"),
                "disclosure_id": f"krx_{disclosure.get('seq')}",
                "title": disclosure.get("disclosureTitl"),
                "disclosure_type": disclosure.get("disclosureTypeNm"),
                "disclosure_date": disclosure.get("disclosureDate").replace("/", ""),
                "url": disclosure.get("disclosureUrl", ""),
                "submitted_at": datetime.now().isoformat(),
                "raw_data": disclosure
            }
            processed_disclosures.append(processed_disclosure)
        
        return processed_disclosures
    
    async def store(self, data: List[Dict[str, Any]]) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        수집된 공시정보 저장 로직 구현
        
        Args:
            data: 수집된 공시정보 목록
            
        Returns:
            tuple: (저장 위치, 메타데이터)
        """
        if not data:
            logger.warning("저장할 공시정보가 없습니다")
            return None, {"count": 0}
        
        # 데이터 저장 서비스로 전송 (메시지 큐 또는 API 호출)
        # 실제 구현에서는 RabbitMQ 또는 REST API를 통해 데이터 저장 서비스로 전송
        
        # 예시: 저장 위치 및 메타데이터 생성
        storage_location = f"disclosures/{self.source}/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        metadata = {
            "count": len(data),
            "source": self.source,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "corp_code": self.corp_code if self.corp_code else "all",
            "disclosure_type": self.disclosure_type if self.disclosure_type else "all"
        }
        
        logger.info(f"공시정보 저장 완료: {len(data)}개, 위치: {storage_location}")
        return storage_location, metadata 