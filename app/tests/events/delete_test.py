import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from app.events.authorizers import (
    EVENT_NOT_BELONG_TO_USER_MSG,
    USER_ROLE_NOT_ORGANIZER_MSG,
)
from app.events.models import Event
from app.exceptions import AccessForbiddenException, NotFoundException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import EventFactory, UserFactory
from app.users.enums import UserRole
from sqlalchemy.orm import Session
from fastapi import status


BASE_URL = "/organizer/events"


def url(event_id: int) -> str:
    return f"{BASE_URL}/{event_id}"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.delete(url(1), headers=headers)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_event_not_found(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id + 1), headers=headers)
    response_data = response.json()

    expected_exception = NotFoundException(Event.__name__)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_is_not_organizer(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id), headers=headers)

    response_data = response.json()
    expected_exception = AccessForbiddenException(USER_ROLE_NOT_ORGANIZER_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_current_user_not_event_owner(async_client: AsyncClient):
    current_user = UserFactory()
    other_user = UserFactory()
    event = EventFactory(organizer=other_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id), headers=headers)
    response_data = response.json()

    expected_exception = AccessForbiddenException(EVENT_NOT_BELONG_TO_USER_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine(db_session: Session, async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    assert db_session.scalar(select(func.count()).select_from(Event)) == 1

    response = await async_client.delete(url(event.id), headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert db_session.scalar(select(func.count()).select_from(Event)) == 0
