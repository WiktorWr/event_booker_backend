from pydantic import ValidationError
import pytest
from httpx import AsyncClient
from fastapi import status
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import UserFactory
from datetime import datetime
from app.events.authorizers import USER_ROLE_NOT_ORGANIZER_MSG
from app.exceptions import AccessForbiddenException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from app.events.models import Event
from app.events.schemas import RepresentEventDetails

from app.users.enums import UserRole

URL = "/events"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.post(URL, headers=headers, json={})
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_missing_params(async_client: AsyncClient):
    current_user = UserFactory()
    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.post(URL, headers=headers, json={})
    response_data = response.json()
    errors = response_data["detail"]

    expected_missing_fields = {"title", "event_date", "description"}

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for field in expected_missing_fields:
        assert any(
            error["loc"][-1] == field for error in errors
        ), f"Missing validation error for field: {field}"


@pytest.mark.asyncio
async def test_negative_price(async_client: AsyncClient):
    current_user = UserFactory()
    headers = utils.generate_user_auth_header(current_user.id)

    json_data = {
        "title": "Title",
        "event_date": str(datetime.now()),
        "description": "Description",
        "price": -1,
    }

    response = await async_client.post(URL, headers=headers, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "price"
    assert errors[0]["type"] == "greater_than"


@pytest.mark.asyncio
async def test_negative_capacity(async_client: AsyncClient):
    current_user = UserFactory()
    headers = utils.generate_user_auth_header(current_user.id)

    json_data = {
        "title": "Title",
        "event_date": str(datetime.now()),
        "description": "Description",
        "max_capacity": -1,
    }

    response = await async_client.post(URL, headers=headers, json=json_data)
    response_data = response.json()
    errors = response_data["detail"]

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert len(errors) == 1
    assert errors[0]["loc"][-1] == "max_capacity"
    assert errors[0]["type"] == "greater_than"


@pytest.mark.asyncio
async def test_user_is_not_organizer(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    headers = utils.generate_user_auth_header(current_user.id)

    json_data = {
        "title": "Title",
        "event_date": str(datetime.now()),
        "description": "Description",
    }

    response = await async_client.post(URL, headers=headers, json=json_data)
    response_data = response.json()

    expected_exception = AccessForbiddenException(USER_ROLE_NOT_ORGANIZER_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_is_fine(db_session: Session, async_client: AsyncClient):
    current_user = UserFactory()
    headers = utils.generate_user_auth_header(current_user.id)

    json_data = {
        "title": "Title",
        "event_date": str(datetime.now()),
        "description": "Description",
        "price": 100_000,
        "max_capacity": 10,
    }

    assert db_session.scalar(select(func.count()).select_from(Event)) == 0

    response = await async_client.post(URL, headers=headers, json=json_data)
    response_data = response.json()

    assert response.status_code == 201
    assert db_session.scalar(select(func.count()).select_from(Event)) == 1
    try:
        RepresentEventDetails(**response_data)
    except ValidationError as e:
        pytest.fail(str(e))
