from functools import wraps
from .schemas import RevokeTokenParams
from sqlalchemy.orm import Session
from .models import RevokedToken
from sqlalchemy import select


def validate_token_revoke(fn):
    @wraps(fn)
    def wrapper(params: RevokeTokenParams, db: Session, *args, **kwargs):
        if db.scalar(select(RevokedToken).where(RevokedToken.hash == params.token)):
            return None

        return fn(params, db=db, *args, **kwargs)

    return wrapper
