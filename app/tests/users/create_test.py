from pydantic import ValidationError
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.users.models import User
from app.tests.factories import UserFactory
from app.users.router import router as users_router
from fastapi import status
from sqlalchemy import select, func
from app.users.enums import UserRole
from app.users.schemas import INVALID_USERNAME_ERROR, RepresentUser
from app.exceptions import AlreadyExistsException


@pytest.mark.asyncio
async def test_missing_params(async_client: AsyncClient):
    response = await async_client.post(users_router.prefix, json={})
    response_data = response.json()
    errors = response_data["detail"]

    expected_missing_fields = {"username", "password", "role"}

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for field in expected_missing_fields:
        assert any(
            error["loc"][-1] == field for error in errors
        ), f"Missing validation error for field: {field}"


@pytest.mark.asyncio
async def test_username_too_short(async_client: AsyncClient):
    json_data = {
        "username": "123",
        "password": "Password100!",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == 422
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "username"
    assert errors[0]["type"] == "string_too_short"


@pytest.mark.asyncio
async def test_username_too_long(async_client: AsyncClient):
    json_data = {
        "username": "_______TOO_LONG______________",
        "password": "Password100!",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == 422
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "username"
    assert errors[0]["type"] == "string_too_long"


@pytest.mark.asyncio
async def test_username_invalid_format(async_client: AsyncClient):
    json_data = {
        "username": " ^& invalid ",
        "password": "Password100!",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == 422
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "username"
    assert errors[0]["type"] == "value_error"
    assert INVALID_USERNAME_ERROR in errors[0]["msg"]


@pytest.mark.asyncio
async def test_password_too_short(async_client: AsyncClient):
    json_data = {
        "username": "Usernamer123",
        "password": "short",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == 422
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "password"
    assert errors[0]["type"] == "string_too_short"


@pytest.mark.asyncio
async def test_password_invalid_format(async_client: AsyncClient):
    json_data = {
        "username": "Usernamer123",
        "password": "invalidFormat",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == 422
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "password"
    assert errors[0]["type"] == "value_error"


@pytest.mark.asyncio
async def test_username_already_exists(async_client: AsyncClient):
    user_one = UserFactory()

    json_data = {
        "username": user_one.username,
        "password": "Password100!",
        "role": UserRole.ORGANIZER.value,
    }

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()

    expected_exception = AlreadyExistsException("username")

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_is_fine(db_session: Session, async_client: AsyncClient):
    json_data = {
        "username": "Username1231",
        "password": "Password100!",
        "role": UserRole.ORGANIZER.value,
    }

    assert db_session.scalar(select(func.count()).select_from(User)) == 0

    response = await async_client.post(users_router.prefix, json=json_data)
    response_data = response.json()

    assert response.status_code == 201
    assert db_session.scalar(select(func.count()).select_from(User)) == 1
    try:
        RepresentUser(**response_data)
    except ValidationError as e:
        pytest.fail(str(e))
