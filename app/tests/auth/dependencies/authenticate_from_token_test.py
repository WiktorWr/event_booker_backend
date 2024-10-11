from app.auth.dependencies import authenticate_user_from_token
from sqlalchemy.orm import Session
from app.tests.factories import UserFactory, RevokedTokenFactory
import pytest
from app.auth.exceptions import InvalidTokenException
from datetime import datetime, timedelta
from jose import jwt
from app.auth.config import settings


def test_token_is_invalid(db_session: Session):
    with pytest.raises(InvalidTokenException):
        authenticate_user_from_token(db=db_session, token="invalid")


def test_token_is_revoked(db_session: Session):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )

    RevokedTokenFactory(hash=access_token)

    with pytest.raises(InvalidTokenException):
        authenticate_user_from_token(db=db_session, token=access_token)


def test_token_is_expired(db_session: Session):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() - timedelta(minutes=60)),
        "sub": str(user.id),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )

    with pytest.raises(InvalidTokenException):
        authenticate_user_from_token(db=db_session, token=access_token)


def test_user_is_not_found(db_session: Session):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id + 1),
    }

    access_token = jwt.encode(
        access_payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    with pytest.raises(InvalidTokenException):
        authenticate_user_from_token(db=db_session, token=access_token)


def test_everything_is_fine(db_session: Session):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id),
    }

    access_token = jwt.encode(
        access_payload, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )

    returned_value = authenticate_user_from_token(db=db_session, token=access_token)

    assert returned_value == user
