from fastapi import HTTPException, status
from app.exceptions import AccessForbiddenException


class AlreadyEnrolledException(HTTPException):
    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        detail = "User is already enrolled for the event"
        super().__init__(status_code=status_code, detail=detail)


class NotEnrolledException(HTTPException):
    def __init__(self):
        status_code = status.HTTP_409_CONFLICT
        detail = "User is not enrolled for the event"
        super().__init__(status_code=status_code, detail=detail)


class UserNotOrganizerException(AccessForbiddenException):
    def __init__(self):
        super().__init__(reason="User role is not organizer")


class UserNotParticipantException(AccessForbiddenException):
    def __init__(self):
        super().__init__(reason="User role is not participant")


class EventNotBelongToUserException(AccessForbiddenException):
    def __init__(self):
        super().__init__(reason="The event does not belong to the current user")
