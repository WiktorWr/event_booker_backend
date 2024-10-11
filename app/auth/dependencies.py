from pydantic import ValidationError
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.dependencies import get_db
from app.users.models import User
from fastapi.security import OAuth2PasswordRequestForm
from .exceptions import InvalidCredentialsException, InvalidTokenException
from .schemas import (
    DataFromRefreshToken,
    RefreshTokenParams,
    RepresentPayload,
)
from jose import jwt, JWTError
from .config import settings
from datetime import datetime
from .models import RevokedToken

from sqlalchemy import select


def get_user_id_from_credentials(
    *,
    params: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
    db: Session = Depends(get_db),
) -> int:
    user = db.scalar(select(User).where(User.username == params.username))

    if user and settings.PASSWORD_CONTEXT.verify(params.password, user.hashed_password):
        return user.id

    raise InvalidCredentialsException()


def authenticate_user_from_token(
    *, db: Session = Depends(get_db), token: str = Depends(settings.OAUTH2_SCHEME)
) -> User:
    try:
        if __is_revoked(token, db=db):
            raise InvalidTokenException()

        payload = RepresentPayload(
            **jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        )

        if __is_expired(payload):
            raise InvalidTokenException()

        user = db.scalar(select(User).where(User.id == int(payload.sub)))

        if user is None:
            raise InvalidTokenException()

        return user

    except (JWTError, ValidationError):
        raise InvalidTokenException()


def get_payload_from_refresh_token(
    params: RefreshTokenParams, *, db: Session = Depends(get_db)
) -> DataFromRefreshToken:
    try:
        if __is_revoked(params.refresh_token, db):
            raise InvalidTokenException()

        refresh_payload = RepresentPayload(
            **jwt.decode(
                params.refresh_token,
                settings.JWT_REFRESH_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        )

        if __is_expired(refresh_payload):
            raise InvalidTokenException()

        if __is_revoked(refresh_payload.sub, db):
            raise InvalidTokenException()

        access_payload = RepresentPayload(
            **jwt.decode(
                refresh_payload.sub,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        )
    except (JWTError, ValidationError):
        raise InvalidTokenException()

    return DataFromRefreshToken(
        access_payload=access_payload,
        refresh_payload=refresh_payload,
        received_refresh_token=params.refresh_token,
    )


### COMMON HELPER FUNCTIONS ###


def __is_revoked(token: str, db: Session) -> bool:
    return db.scalar(select(RevokedToken).where(RevokedToken.hash == token)) is not None


def __is_expired(payload: RepresentPayload) -> bool:
    return payload.expires_at.replace(tzinfo=None) < datetime.now()
