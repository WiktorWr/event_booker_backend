from pydantic import ValidationError
import pytest
from httpx import AsyncClient
from app.auth.schemas import RepresentJWT
from app.tests.factories import RevokedTokenFactory
from app.auth.router import router as auth_router
from fastapi import status
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import UserFactory
from datetime import datetime, timedelta
from jose import jwt
from app.auth.config import settings
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.auth.models import RevokedToken

REFRESH_URL = f"{auth_router.prefix}/refresh"


@pytest.mark.asyncio
async def test_missing_params(async_client: AsyncClient):
    response = await async_client.post(REFRESH_URL, json={})
    response_data = response.json()
    errors = response_data["detail"]

    expected_missing_fields = {"refresh_token"}

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for field in expected_missing_fields:
        assert any(
            error["loc"][-1] == field for error in errors
        ), f"Missing validation error for field: {field}"


@pytest.mark.asyncio
async def test_refresh_token_is_revoked(async_client: AsyncClient):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )
    refresh_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": access_token,
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_REFRESH_SECRET_KEY,
    )

    RevokedTokenFactory(hash=refresh_token)

    json_data = {"refresh_token": refresh_token}

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_access_token_is_revoked(async_client: AsyncClient):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )
    refresh_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": access_token,
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_REFRESH_SECRET_KEY,
    )

    RevokedTokenFactory(hash=access_token)

    json_data = {"refresh_token": refresh_token}

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_refresh_token_is_invalid(async_client: AsyncClient):
    json_data = {"refresh_token": "invalid"}

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_refresh_token_is_expired(async_client: AsyncClient):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() - timedelta(minutes=60)),
        "sub": user.id,
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )
    refresh_payload = {
        "expires_at": str(datetime.now() - timedelta(minutes=60)),
        "sub": access_token,
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_REFRESH_SECRET_KEY,
    )

    json_data = {"refresh_token": refresh_token}

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_access_token_is_invalid(async_client: AsyncClient):
    refresh_payload = {
        "expires_at": str(datetime.now() - timedelta(minutes=60)),
        "sub": "invalid",
    }
    refresh_token = jwt.encode(
        refresh_payload,
        "key",
    )

    json_data = {"refresh_token": refresh_token}

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_is_fine(db_session: Session, async_client: AsyncClient):
    user = UserFactory()

    access_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": str(user.id),
    }
    access_token = jwt.encode(
        access_payload,
        settings.JWT_SECRET_KEY,
    )
    refresh_payload = {
        "expires_at": str(datetime.now() + timedelta(minutes=60)),
        "sub": access_token,
    }
    refresh_token = jwt.encode(
        refresh_payload,
        settings.JWT_REFRESH_SECRET_KEY,
    )

    json_data = {"refresh_token": refresh_token}

    assert db_session.scalar(select(func.count()).select_from(RevokedToken)) == 0

    response = await async_client.post(REFRESH_URL, json=json_data)
    response_data = response.json()

    db_revoked_hashes = db_session.scalars(select(RevokedToken.hash)).all()

    assert response.status_code == status.HTTP_201_CREATED
    assert set(db_revoked_hashes) == set([access_token, refresh_token])

    try:
        RepresentJWT(**response_data)
    except ValidationError as e:
        pytest.fail(str(e))
