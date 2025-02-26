"""
날짜 관련 유틸리티 함수
"""
from datetime import datetime, timedelta
from typing import Optional, Tuple


def get_date_range(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    days: int = 7,
    date_format: str = "%Y-%m-%d",
) -> Tuple[str, str]:
    """
    시작일과 종료일 범위를 반환
    
    Args:
        start_date: 시작일 (YYYY-MM-DD 형식)
        end_date: 종료일 (YYYY-MM-DD 형식)
        days: 기본 일수 (시작일이 없는 경우)
        date_format: 날짜 형식
        
    Returns:
        Tuple[str, str]: (시작일, 종료일) 튜플
    """
    if end_date is None:
        end_dt = datetime.utcnow()
    else:
        end_dt = datetime.strptime(end_date, date_format)
    
    if start_date is None:
        start_dt = end_dt - timedelta(days=days)
    else:
        start_dt = datetime.strptime(start_date, date_format)
    
    return start_dt.strftime(date_format), end_dt.strftime(date_format)


def parse_date(date_str: str, date_format: str = "%Y-%m-%d") -> datetime:
    """
    문자열을 datetime 객체로 변환
    
    Args:
        date_str: 날짜 문자열
        date_format: 날짜 형식
        
    Returns:
        datetime: 변환된 datetime 객체
    """
    return datetime.strptime(date_str, date_format)


def format_date(dt: datetime, date_format: str = "%Y-%m-%d") -> str:
    """
    datetime 객체를 문자열로 변환
    
    Args:
        dt: datetime 객체
        date_format: 날짜 형식
        
    Returns:
        str: 변환된 날짜 문자열
    """
    return dt.strftime(date_format)


def get_quarter_start_end(year: int, quarter: int) -> Tuple[datetime, datetime]:
    """
    특정 연도와 분기의 시작일과 종료일 반환
    
    Args:
        year: 연도
        quarter: 분기 (1-4)
        
    Returns:
        Tuple[datetime, datetime]: (시작일, 종료일) 튜플
    """
    if quarter < 1 or quarter > 4:
        raise ValueError("분기는 1에서 4 사이의 값이어야 합니다")
    
    month = (quarter - 1) * 3 + 1
    
    start_date = datetime(year, month, 1)
    
    if quarter < 4:
        end_date = datetime(year, month + 3, 1) - timedelta(days=1)
    else:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    
    return start_date, end_date 