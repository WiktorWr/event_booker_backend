from functools import wraps
from .exceptions import (
    AlreadyEnrolledException,
    EventNotBelongToUserException,
    NotEnrolledException,
    UserNotOrganizerException,
    UserNotParticipantException,
)
from app.users.models import User
from app.users.enums import UserRole
from .models import Event, Enrollment
from sqlalchemy.orm import Session
from sqlalchemy import select


def current_user_role_is_organizer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")

        if user.role != UserRole.ORGANIZER:
            raise UserNotOrganizerException()

        return fn(*args, **kwargs)

    return wrapper


def current_user_role_is_participant(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")

        if user.role != UserRole.PARTICIPANT:
            raise UserNotParticipantException()

        return fn(*args, **kwargs)

    return wrapper


def event_belongs_to_organizer(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user: User = kwargs.get("current_user")
        event: Event = kwargs.get("event")

        if event.organizer_id != user.id:
            raise EventNotBelongToUserException()

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
