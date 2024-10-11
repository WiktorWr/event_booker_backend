from sqlalchemy.orm import Session
from .schemas import CreateEventParams
from functools import wraps
from app.users.models import User
from app.users.enums import UserRole
from app.exceptions import AccessForbiddenException

USER_NOT_ORGANIZER_MSG = "User role is not organizer"


def authorize_event_create(fn):
    @wraps(fn)
    def wrapper(
        params: CreateEventParams, db: Session, current_user: User, *args, **kwargs
    ):
        if current_user.role != UserRole.ORGANIZER:
            raise AccessForbiddenException(USER_NOT_ORGANIZER_MSG)

        return fn(params, db=db, current_user=current_user, *args, **kwargs)

    return wrapper
