"""
JSON 관련 유틸리티 함수
"""
import json
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID


class JSONEncoder(json.JSONEncoder):
    """
    확장된 JSON 인코더
    datetime, date, UUID 등의 객체를 JSON으로 직렬화
    """
    
    def default(self, obj: Any) -> Any:
        """
        기본 직렬화 메서드 오버라이드
        
        Args:
            obj: 직렬화할 객체
            
        Returns:
            Any: 직렬화된 값
        """
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        return super().default(obj)


def to_json(obj: Any) -> str:
    """
    객체를 JSON 문자열로 변환
    
    Args:
        obj: 변환할 객체
        
    Returns:
        str: JSON 문자열
    """
    return json.dumps(obj, cls=JSONEncoder)


def from_json(json_str: str) -> Any:
    """
    JSON 문자열을 객체로 변환
    
    Args:
        json_str: JSON 문자열
        
    Returns:
        Any: 변환된 객체
    """
    return json.loads(json_str)


def parse_json_parameters(
    parameters: Optional[Union[str, Dict[str, Any]]]
) -> Dict[str, Any]:
    """
    JSON 매개변수 파싱
    
    Args:
        parameters: JSON 문자열 또는 딕셔너리
        
    Returns:
        Dict[str, Any]: 파싱된 매개변수
    """
    if not parameters:
        return {}
    
    if isinstance(parameters, dict):
        return parameters
    
    try:
        return json.loads(parameters)
    except json.JSONDecodeError:
        return {} 