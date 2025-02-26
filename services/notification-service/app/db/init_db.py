"""
데이터베이스 초기화 모듈
"""
import logging

from sqlalchemy.exc import SQLAlchemyError

from app.db.session import Base, engine

logger = logging.getLogger(__name__)


async def init_db() -> None:
    """
    데이터베이스 초기화 함수
    테이블 생성 및 초기 데이터 설정
    """
    try:
        # 모든 모델의 테이블 생성
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("데이터베이스 테이블 생성 완료")
        
        # 초기 데이터 설정 (필요한 경우)
        # await create_initial_data()
        
    except SQLAlchemyError as e:
        logger.error(f"데이터베이스 초기화 중 오류 발생: {str(e)}")
        raise


async def create_initial_data() -> None:
    """
    초기 데이터 생성 함수
    필요한 경우 기본 데이터를 데이터베이스에 추가
    """
    # 예: 기본 알림 템플릿 추가
    # from app.db.session import SessionLocal
    # from app.models.notification_template import NotificationTemplate
    # 
    # async with SessionLocal() as db:
    #     try:
    #         # 기본 이메일 템플릿
    #         email_template = NotificationTemplate(
    #             name="기본 이메일 템플릿",
    #             type="email",
    #             subject="{{title}}",
    #             content="""
    #             <html>
    #             <body>
    #                 <h1>{{title}}</h1>
    #                 <p>{{message}}</p>
    #             </body>
    #             </html>
    #             """,
    #             is_default=True
    #         )
    #         db.add(email_template)
    #         
    #         await db.commit()
    #         logger.info("초기 알림 템플릿 생성 완료")
    #     
    #     except SQLAlchemyError as e:
    #         await db.rollback()
    #         logger.error(f"초기 데이터 생성 중 오류 발생: {str(e)}")
    
    pass 