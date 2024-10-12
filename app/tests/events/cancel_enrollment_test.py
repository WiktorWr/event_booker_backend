import pytest
from httpx import AsyncClient
from app.events.exceptions import NotEnrolledException, UserNotParticipantException
from app.events.models import Enrollment, Event
from app.exceptions import NotFoundException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import EnrollmentFactory, UserFactory, EventFactory
from app.users.enums import UserRole
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from fastapi import status


def url(event_id: int) -> str:
    return f"/participant/events/{event_id}/cancel"


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
    event = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id + 1), headers=headers)
    response_data = response.json()

    expected_exception = NotFoundException(Event.__name__)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_is_participant(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id), headers=headers)

    response_data = response.json()
    expected_exception = UserNotParticipantException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_not_enrolled(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.delete(url(event.id), headers=headers)

    response_data = response.json()
    expected_exception = NotEnrolledException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine(db_session: Session, async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory()
    EnrollmentFactory(participant=current_user, event=event)

    headers = utils.generate_user_auth_header(current_user.id)

    assert db_session.scalar(select(func.count()).select_from(Enrollment)) == 1

    response = await async_client.delete(url(event.id), headers=headers)

    assert response.status_code == status.HTTP_200_OK
    assert db_session.scalar(select(func.count()).select_from(Enrollment)) == 0
