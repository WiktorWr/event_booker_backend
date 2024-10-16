from sqlalchemy.orm import Session
from .models import User
from .schemas import CreateUserParams
from .exceptions import UsernameAlreadyExistsException
from functools import wraps
from sqlalchemy import select


def validate_user_create(fn):
    @wraps(fn)
    def wrapper(params: CreateUserParams, db: Session, *args, **kwargs):
        if db.scalar(select(User).where(User.username == params.username)):
            raise UsernameAlreadyExistsException()

        return fn(params, db, *args, **kwargs)

    return wrapper
