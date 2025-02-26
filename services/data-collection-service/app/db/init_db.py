"""
데이터베이스 초기화 모듈
"""
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db.session import Base, engine

logger = logging.getLogger(__name__)


def init_db() -> None:
    """
    데이터베이스 초기화 함수
    테이블 생성 및 초기 데이터 설정
    """
    try:
        # 모든 모델의 테이블 생성
        Base.metadata.create_all(bind=engine)
        logger.info("데이터베이스 테이블 생성 완료")
        
        # 초기 데이터 설정 (필요한 경우)
        # create_initial_data()
        
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {str(e)}")
        raise


def create_initial_data() -> None:
    """
    초기 데이터 생성 함수
    필요한 경우 기본 데이터를 데이터베이스에 추가
    """
    # 예: 기본 수집 작업 추가
    # from app.db.session import SessionLocal
    # from app.models.collection_task import CollectionTask, CollectionType, TaskStatus
    # from datetime import datetime, timedelta
    # 
    # db = SessionLocal()
    # try:
    #     # 기본 주식 정보 수집 작업
    #     stock_info_task = CollectionTask(
    #         collection_type=CollectionType.STOCK_INFO,
    #         status=TaskStatus.PENDING,
    #         parameters=json.dumps({"symbol": "AAPL"}),
    #         scheduled_at=datetime.utcnow() + timedelta(minutes=5),
    #         is_recurring=True,
    #         interval_minutes=1440,  # 24시간마다
    #     )
    #     db.add(stock_info_task)
    #     
    #     # 기본 주식 가격 수집 작업
    #     stock_price_task = CollectionTask(
    #         collection_type=CollectionType.STOCK_PRICE,
    #         status=TaskStatus.PENDING,
    #         parameters=json.dumps({"symbol": "AAPL", "interval": "1d"}),
    #         scheduled_at=datetime.utcnow() + timedelta(minutes=10),
    #         is_recurring=True,
    #         interval_minutes=60,  # 1시간마다
    #     )
    #     db.add(stock_price_task)
    #     
    #     db.commit()
    #     logger.info("초기 데이터 생성 완료")
    # 
    # except SQLAlchemyError as e:
    #     db.rollback()
    #     logger.error(f"초기 데이터 생성 중 오류 발생: {str(e)}")
    # 
    # finally:
    #     db.close()
    
    pass 