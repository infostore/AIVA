"""
데이터 수집기 팩토리
"""
import logging
from typing import Optional, Type

from sqlalchemy.orm import Session

from app.collectors.base import BaseCollector
from app.collectors.stock_info_collector import StockInfoCollector
from app.collectors.stock_price_collector import StockPriceCollector
from app.collectors.disclosure_collector import DisclosureCollector
from app.models.collection_task import CollectionTask, CollectionType

logger = logging.getLogger(__name__)


class CollectorFactory:
    """
    데이터 수집기 팩토리 클래스
    수집 작업 유형에 따라 적절한 수집기 인스턴스를 생성
    """
    
    @staticmethod
    def create_collector(db: Session, task: CollectionTask) -> Optional[BaseCollector]:
        """
        수집 작업 유형에 따라 적절한 수집기 인스턴스 생성
        
        Args:
            db: 데이터베이스 세션
            task: 수집 작업 객체
            
        Returns:
            Optional[BaseCollector]: 수집기 인스턴스 또는 None
        """
        collector_map = {
            CollectionType.STOCK_PRICE: StockPriceCollector,
            CollectionType.STOCK_INFO: StockInfoCollector,
            CollectionType.DISCLOSURE: DisclosureCollector,
            # 추가 수집기 유형은 여기에 매핑
        }
        
        collector_class = collector_map.get(task.collection_type)
        
        if not collector_class:
            logger.error(f"지원되지 않는 수집 유형: {task.collection_type}")
            return None
        
        logger.info(f"수집기 생성: type={task.collection_type}, id={task.id}")
        return collector_class(db, task) 