import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from app.auth.exceptions import InvalidTokenException
from app.events.authorizers import USER_ROLE_NOT_PARTICIPANT_MSG
from app.events.exceptions import AlreadyEnrolledException
from app.events.models import Event, Enrollment
from app.exceptions import AccessForbiddenException, NotFoundException
from app.tests import utils
from app.tests.factories import EventFactory, UserFactory, EnrollmentFactory
from app.users.enums import UserRole
from sqlalchemy.orm import Session
from fastapi import status


def url(event_id: int) -> str:
    return f"/events/{event_id}/enroll"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.post(url(1), headers=headers, json={})
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_event_not_found(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.post(url(event.id + 1), headers=headers)
    response_data = response.json()

    expected_exception = NotFoundException(Event.__name__)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_not_participant(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.post(url(event.id), headers=headers)
    response_data = response.json()

    expected_exception = AccessForbiddenException(USER_ROLE_NOT_PARTICIPANT_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_already_enrolled(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory(organizer=current_user)
    EnrollmentFactory(participant=current_user, event=event)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.post(url(event.id), headers=headers)
    response_data = response.json()

    expected_exception = AlreadyEnrolledException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_is_fine(db_session: Session, async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    assert db_session.scalar(select(func.count()).select_from(Enrollment)) == 0

    response = await async_client.post(url(event.id), headers=headers)

    assert response.status_code == status.HTTP_201_CREATED
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(Enrollment)
            .where(
                Enrollment.participant_id == current_user.id,
                Enrollment.event_id == event.id,
            )
        )
        == 1
    )
