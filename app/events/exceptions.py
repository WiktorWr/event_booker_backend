from fastapi import HTTPException, status


class AlreadyEnrolledException(HTTPException):
    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        detail = "User is already enrolled for the event"
        super().__init__(status_code=status_code, detail=detail)
