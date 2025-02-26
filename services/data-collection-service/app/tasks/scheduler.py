"""
작업 스케줄러 모듈
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.collectors.factory import create_collector
from app.config import settings
from app.db.session import SessionLocal
from app.models.collection_task import CollectionTask, TaskStatus

logger = logging.getLogger(__name__)


class TaskScheduler:
    """
    작업 스케줄러 클래스
    """
    
    def __init__(self):
        """
        스케줄러 초기화
        """
        self.running = False
        self.active_tasks = set()
        self.max_concurrent_tasks = settings.MAX_CONCURRENT_COLLECTIONS
    
    async def start(self):
        """
        스케줄러 시작
        """
        if self.running:
            logger.warning("스케줄러가 이미 실행 중입니다")
            return
        
        self.running = True
        logger.info("작업 스케줄러 시작")
        
        while self.running:
            try:
                # 실행할 작업 가져오기
                tasks = await self._get_pending_tasks()
                
                if tasks:
                    logger.info(f"{len(tasks)}개의 대기 중인 작업을 찾았습니다")
                    
                    # 동시 실행 가능한 작업 수 계산
                    available_slots = self.max_concurrent_tasks - len(self.active_tasks)
                    tasks_to_run = tasks[:available_slots]
                    
                    # 작업 실행
                    for task in tasks_to_run:
                        asyncio.create_task(self._execute_task(task))
                
                # 일정 시간 대기
                await asyncio.sleep(10)  # 10초마다 확인
                
            except Exception as e:
                logger.error(f"스케줄러 실행 중 오류 발생: {str(e)}")
                await asyncio.sleep(30)  # 오류 발생 시 30초 대기
    
    async def stop(self):
        """
        스케줄러 중지
        """
        logger.info("작업 스케줄러 중지")
        self.running = False
    
    async def _get_pending_tasks(self) -> List[CollectionTask]:
        """
        실행 대기 중인 작업 목록 조회
        
        Returns:
            List[CollectionTask]: 실행할 작업 목록
        """
        async with SessionLocal() as db:
            # 현재 시간 이전에 예약된 대기 중인 작업 조회
            now = datetime.utcnow()
            stmt = select(CollectionTask).where(
                and_(
                    CollectionTask.status == TaskStatus.PENDING,
                    CollectionTask.scheduled_at <= now
                )
            ).order_by(CollectionTask.scheduled_at)
            
            result = await db.execute(stmt)
            tasks = result.scalars().all()
            
            # 작업 상태 업데이트
            for task in tasks:
                task.status = TaskStatus.RUNNING
                task.started_at = now
            
            await db.commit()
            
            return tasks
    
    async def _execute_task(self, task: CollectionTask):
        """
        작업 실행
        
        Args:
            task: 실행할 작업
        """
        task_id = task.id
        self.active_tasks.add(task_id)
        
        try:
            logger.info(f"작업 실행 시작: {task_id} (유형: {task.collection_type})")
            
            # 수집기 생성 및 실행
            collector = create_collector(task.collection_type, task.parameters)
            result = await collector.collect()
            
            # 결과 저장
            async with SessionLocal() as db:
                db_task = await self._get_task_by_id(db, task_id)
                if not db_task:
                    logger.error(f"작업을 찾을 수 없음: {task_id}")
                    return
                
                # 작업 결과 업데이트
                db_task.status = TaskStatus.COMPLETED
                db_task.completed_at = datetime.utcnow()
                db_task.result = result
                
                # 반복 작업인 경우 다음 실행 예약
                if db_task.is_recurring and db_task.interval_minutes:
                    next_task = CollectionTask(
                        collection_type=db_task.collection_type,
                        parameters=db_task.parameters,
                        status=TaskStatus.PENDING,
                        scheduled_at=datetime.utcnow() + timedelta(minutes=db_task.interval_minutes),
                        is_recurring=True,
                        interval_minutes=db_task.interval_minutes
                    )
                    db.add(next_task)
                    logger.info(f"다음 반복 작업 예약: {db_task.collection_type} ({db_task.interval_minutes}분 후)")
                
                await db.commit()
                
            logger.info(f"작업 실행 완료: {task_id}")
            
        except Exception as e:
            logger.error(f"작업 실행 중 오류 발생: {task_id}, 오류: {str(e)}")
            
            # 작업 상태 업데이트 (실패)
            try:
                async with SessionLocal() as db:
                    db_task = await self._get_task_by_id(db, task_id)
                    if db_task:
                        db_task.status = TaskStatus.FAILED
                        db_task.error = str(e)
                        await db.commit()
            except Exception as update_error:
                logger.error(f"작업 상태 업데이트 중 오류 발생: {str(update_error)}")
        
        finally:
            # 활성 작업 목록에서 제거
            self.active_tasks.discard(task_id)
    
    async def _get_task_by_id(self, db: AsyncSession, task_id: int) -> Optional[CollectionTask]:
        """
        ID로 작업 조회
        
        Args:
            db: 데이터베이스 세션
            task_id: 작업 ID
            
        Returns:
            Optional[CollectionTask]: 작업 객체 또는 None
        """
        result = await db.execute(select(CollectionTask).where(CollectionTask.id == task_id))
        return result.scalar_one_or_none()


# 전역 스케줄러 인스턴스
scheduler = TaskScheduler()


async def start_scheduler():
    """
    스케줄러 시작 함수
    """
    await scheduler.start()


async def stop_scheduler():
    """
    스케줄러 중지 함수
    """
    await scheduler.stop() 