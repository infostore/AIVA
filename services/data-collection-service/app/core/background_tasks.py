"""
백그라운드 작업 처리 모듈
"""
import asyncio
import logging
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.collectors.factory import CollectorFactory
from app.db.session import SessionLocal
from app.models.collection_task import CollectionTask

logger = logging.getLogger(__name__)

# 실행 중인 작업 추적을 위한 딕셔너리
running_tasks: Dict[int, asyncio.Task] = {}


def add_background_task(task_id: int) -> None:
    """
    백그라운드 작업 큐에 작업 추가
    
    Args:
        task_id: 수집 작업 ID
    """
    if task_id in running_tasks and not running_tasks[task_id].done():
        logger.warning(f"작업 ID {task_id}는 이미 실행 중입니다")
        return
    
    # 백그라운드 작업 생성 및 시작
    task = asyncio.create_task(execute_collection_task(task_id))
    running_tasks[task_id] = task
    
    logger.info(f"백그라운드 작업 추가: task_id={task_id}")


async def execute_collection_task(task_id: int) -> None:
    """
    데이터 수집 작업 실행
    
    Args:
        task_id: 수집 작업 ID
    """
    db = SessionLocal()
    try:
        # 작업 조회
        task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
        if not task:
            logger.error(f"작업 ID {task_id}를 찾을 수 없습니다")
            return
        
        logger.info(f"작업 실행 시작: id={task.id}, type={task.collection_type}")
        
        # 수집기 생성
        collector = CollectorFactory.create_collector(db, task)
        if not collector:
            logger.error(f"작업 ID {task_id}에 대한 수집기를 생성할 수 없습니다")
            return
        
        # 수집 작업 실행
        await collector.execute()
        
        logger.info(f"작업 실행 완료: id={task.id}, type={task.collection_type}")
        
        # 반복 작업인 경우 다음 실행 예약
        if task.is_recurring and task.interval_minutes:
            # 실제 구현에서는 스케줄러를 사용하여 다음 실행 예약
            logger.info(f"반복 작업 다음 실행 예약: id={task.id}, interval={task.interval_minutes}분")
    
    except Exception as e:
        logger.exception(f"작업 실행 중 오류 발생: id={task_id}, error={str(e)}")
    
    finally:
        db.close()
        # 실행 완료된 작업은 추적 딕셔너리에서 제거
        if task_id in running_tasks:
            del running_tasks[task_id]


async def get_running_tasks() -> List[int]:
    """
    현재 실행 중인 작업 ID 목록 반환
    
    Returns:
        List[int]: 실행 중인 작업 ID 목록
    """
    # 완료된 작업 정리
    for task_id in list(running_tasks.keys()):
        if running_tasks[task_id].done():
            del running_tasks[task_id]
    
    return list(running_tasks.keys()) 