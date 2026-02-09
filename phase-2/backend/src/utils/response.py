"""Standard response formatting"""
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel


class MetaInfo(BaseModel):
    """Metadata for API responses"""

    timestamp: str
    request_id: str


class ErrorInfo(BaseModel):
    """Error information"""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class APIResponse(BaseModel):
    """Standard API response envelope"""

    data: Optional[Any] = None
    meta: MetaInfo
    error: Optional[ErrorInfo] = None

    @staticmethod
    def success(data: Any = None) -> Dict[str, Any]:
        """Create a success response"""
        return {
            "data": data,
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": str(uuid4()),
            },
            "error": None,
        }

    @staticmethod
    def error(code: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create an error response"""
        return {
            "data": None,
            "meta": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "request_id": str(uuid4()),
            },
            "error": {
                "code": code,
                "message": message,
                "details": details,
            },
        }
