from pydantic import ValidationError
import pytest
from httpx import AsyncClient
from app.tests.factories import UserFactory
from app.auth.exceptions import InvalidCredentialsException
from app.auth.router import router as auth_router
from fastapi import status
from app.auth.schemas import RepresentJWT
from app.auth.config import settings as auth_settings


@pytest.mark.asyncio
async def test_missing_params(async_client: AsyncClient):
    response = await async_client.post(auth_router.prefix, json={})
    response_data = response.json()
    errors = response_data["detail"]

    expected_missing_fields = {"username", "password"}

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for field in expected_missing_fields:
        assert any(
            error["loc"][-1] == field for error in errors
        ), f"Missing validation error for field: {field}"


@pytest.mark.asyncio
async def test_user_not_found(async_client: AsyncClient):
    json_data = {"username": "username", "password": "Password100!"}

    response = await async_client.post(auth_router.prefix, data=json_data)
    response_data = response.json()

    expected_exception = InvalidCredentialsException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_invalid_password(async_client: AsyncClient):
    user = UserFactory(
        hashed_password=auth_settings.PASSWORD_CONTEXT.hash("Password100!")
    )

    json_data = {"username": user.username, "password": "Password100$"}

    response = await async_client.post(auth_router.prefix, data=json_data)
    response_data = response.json()

    expected_exception = InvalidCredentialsException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine(async_client: AsyncClient):
    user = UserFactory(
        hashed_password=auth_settings.PASSWORD_CONTEXT.hash("Password100!")
    )

    json_data = {"username": user.username, "password": "Password100!"}

    response = await async_client.post(auth_router.prefix, data=json_data)
    response_data = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    try:
        RepresentJWT(**response_data)
    except ValidationError as e:
        pytest.fail(str(e))
