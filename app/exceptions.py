from fastapi import HTTPException, status
from typing import Optional


class AlreadyExistsException(HTTPException):
    def __init__(self, key: str):
        status_code = status.HTTP_409_CONFLICT
        detail = f"Given {key} already exists"
        super().__init__(status_code=status_code, detail=detail)


class AccessForbiddenException(HTTPException):
    def __init__(self, reason: Optional[str] = None):
        status_code = status.HTTP_403_FORBIDDEN
        detail = f"Access Forbidden: {reason}." if reason else "Access Forbidden."
        super().__init__(status_code=status_code, detail=detail)
