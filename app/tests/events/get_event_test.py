from pydantic import ValidationError
import pytest
from httpx import AsyncClient
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import UserFactory, EventFactory
from app.users.enums import UserRole
from app.exceptions import AccessForbiddenException, NotFoundException
from app.events.authorizers import (
    USER_ROLE_NOT_PARTICIPANT_MSG,
)
from app.events.models import Event
from fastapi import status
from app.events.schemas import RepresentEventDetails


BASE_URL = "/events"


def url(event_id: int) -> str:
    return f"{BASE_URL}/{event_id}"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.get(url(1), headers=headers)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_not_participant(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(url(event.id), headers=headers)
    response_data = response.json()

    expected_exception = AccessForbiddenException(USER_ROLE_NOT_PARTICIPANT_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_event_not_found(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(url(event.id + 1), headers=headers)
    response_data = response.json()

    expected_exception = NotFoundException(Event.__name__)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(url(event.id), headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    try:
        RepresentEventDetails(**response_data)
    except ValidationError as e:
        pytest.fail(str(e))
