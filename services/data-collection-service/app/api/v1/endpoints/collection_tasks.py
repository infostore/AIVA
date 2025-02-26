"""
데이터 수집 작업 API 엔드포인트
"""
import logging
from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api import deps
from app.collectors.factory import CollectorFactory
from app.core.background_tasks import add_background_task
from app.models.collection_task import CollectionTask, CollectionType, TaskStatus
from app.schemas.collection_task import (
    CollectionTask as CollectionTaskSchema,
    CollectionTaskCreate,
    CollectionTaskList,
    CollectionTaskUpdate,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CollectionTaskSchema, status_code=status.HTTP_201_CREATED)
async def create_collection_task(
    *,
    db: Session = Depends(deps.get_db),
    task_in: CollectionTaskCreate,
) -> Any:
    """
    새 데이터 수집 작업 생성
    """
    # 작업 생성
    db_task = CollectionTask(
        collection_type=task_in.collection_type,
        parameters=task_in.parameters,
        scheduled_at=task_in.scheduled_at,
        status=TaskStatus.PENDING,
        is_recurring=task_in.is_recurring,
        interval_minutes=task_in.interval_minutes,
        max_retries=task_in.max_retries,
        retry_count=0,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    logger.info(f"데이터 수집 작업 생성: id={db_task.id}, type={db_task.collection_type}")
    
    # 즉시 실행해야 하는 경우 백그라운드 작업으로 추가
    if not task_in.scheduled_at or task_in.scheduled_at <= datetime.utcnow():
        add_background_task(db_task.id)
    
    return db_task


@router.get("/", response_model=CollectionTaskList)
async def list_collection_tasks(
    *,
    db: Session = Depends(deps.get_db),
    status: Optional[TaskStatus] = None,
    collection_type: Optional[CollectionType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """
    데이터 수집 작업 목록 조회
    """
    # 필터 조건 구성
    filters = []
    if status is not None:
        filters.append(CollectionTask.status == status)
    if collection_type is not None:
        filters.append(CollectionTask.collection_type == collection_type)
    
    # 총 개수 조회
    total = db.query(CollectionTask).filter(*filters).count()
    
    # 페이지네이션 적용하여 작업 목록 조회
    tasks = (
        db.query(CollectionTask)
        .filter(*filters)
        .order_by(CollectionTask.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    # 페이지 정보 계산
    page = skip // limit + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1
    
    return {
        "items": tasks,
        "total": total,
        "page": page,
        "size": limit,
        "pages": pages,
    }


@router.get("/{task_id}", response_model=CollectionTaskSchema)
async def get_collection_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
) -> Any:
    """
    데이터 수집 작업 상세 조회
    """
    task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {task_id}인 데이터 수집 작업을 찾을 수 없습니다",
        )
    return task


@router.put("/{task_id}", response_model=CollectionTaskSchema)
async def update_collection_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
    task_in: CollectionTaskUpdate,
) -> Any:
    """
    데이터 수집 작업 업데이트
    """
    task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {task_id}인 데이터 수집 작업을 찾을 수 없습니다",
        )
    
    # 완료된 작업은 수정 불가
    if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="완료되거나 실패한 작업은 수정할 수 없습니다",
        )
    
    # 업데이트 가능한 필드 처리
    update_data = task_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(f"데이터 수집 작업 업데이트: id={task.id}, type={task.collection_type}")
    
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_collection_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
) -> Any:
    """
    데이터 수집 작업 삭제
    """
    task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {task_id}인 데이터 수집 작업을 찾을 수 없습니다",
        )
    
    # 실행 중인 작업은 삭제 불가
    if task.status == TaskStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="실행 중인 작업은 삭제할 수 없습니다",
        )
    
    db.delete(task)
    db.commit()
    
    logger.info(f"데이터 수집 작업 삭제: id={task_id}")
    
    return None


@router.post("/{task_id}/execute", response_model=CollectionTaskSchema)
async def execute_collection_task(
    *,
    db: Session = Depends(deps.get_db),
    task_id: int,
) -> Any:
    """
    데이터 수집 작업 즉시 실행
    """
    task = db.query(CollectionTask).filter(CollectionTask.id == task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {task_id}인 데이터 수집 작업을 찾을 수 없습니다",
        )
    
    # 이미 실행 중인 작업은 재실행 불가
    if task.status == TaskStatus.RUNNING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 실행 중인 작업입니다",
        )
    
    # 백그라운드 작업으로 추가
    add_background_task(task.id)
    
    # 상태 업데이트
    task.status = TaskStatus.PENDING
    db.add(task)
    db.commit()
    db.refresh(task)
    
    logger.info(f"데이터 수집 작업 실행 요청: id={task.id}, type={task.collection_type}")
    
    return task 