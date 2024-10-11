from fastapi import HTTPException, status


class AlreadyExistsException(HTTPException):
    def __init__(self, key: str):
        status_code = status.HTTP_409_CONFLICT
        detail = f"Given {key} already exists"
        super().__init__(status_code=status_code, detail=detail)
