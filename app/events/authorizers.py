from functools import wraps
from .exceptions import AlreadyEnrolledException, NotEnrolledException
from app.users.models import User
from app.users.enums import UserRole
from app.exceptions import AccessForbiddenException
from .models import Event, Enrollment
from sqlalchemy.orm import Session
from sqlalchemy import select

USER_ROLE_NOT_ORGANIZER_MSG = "User role is not organizer"
USER_ROLE_NOT_PARTICIPANT_MSG = "User role is not participant"
EVENT_NOT_BELONG_TO_USER_MSG = "The event does not belong to the current user"


def current_user_role_is_organizer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")

        if user.role != UserRole.ORGANIZER:
            raise AccessForbiddenException(USER_ROLE_NOT_ORGANIZER_MSG)

        return fn(*args, **kwargs)

    return wrapper


def current_user_role_is_participant(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")

        if user.role != UserRole.PARTICIPANT:
            raise AccessForbiddenException(USER_ROLE_NOT_PARTICIPANT_MSG)

        return fn(*args, **kwargs)

    return wrapper


def event_belongs_to_organizer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")
        event: Event = kwargs.get("event")

        if event.organizer_id != user.id:
            raise AccessForbiddenException(EVENT_NOT_BELONG_TO_USER_MSG)

        return fn(*args, **kwargs)

    return wrapper


def participant_is_not_enrolled(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")
        event: Event = kwargs.get("event")
        db: Session = kwargs.get("db")

        enrollemnt = db.scalar(
            select(Enrollment).where(
                Enrollment.participant_id == user.id, Enrollment.event_id == event.id
            )
        )

        if enrollemnt is not None:
            raise AlreadyEnrolledException()

        return fn(*args, **kwargs)

    return wrapper


def participant_is_enrolled(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")
        event: Event = kwargs.get("event")
        db: Session = kwargs.get("db")

        enrollemnt = db.scalar(
            select(Enrollment).where(
                Enrollment.participant_id == user.id, Enrollment.event_id == event.id
            )
        )

        if enrollemnt is None:
            raise NotEnrolledException()

        return fn(*args, **kwargs)

    return wrapper
