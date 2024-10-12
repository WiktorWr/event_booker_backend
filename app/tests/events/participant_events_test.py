import pytest
from httpx import AsyncClient
from app.events.authorizers import USER_ROLE_NOT_PARTICIPANT_MSG
from app.exceptions import AccessForbiddenException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import EnrollmentFactory, UserFactory, EventFactory
from fastapi import status

from app.users.enums import UserRole


URL = "/participant/events"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_not_participant(async_client: AsyncClient):
    current_user = UserFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    expected_exception = AccessForbiddenException(USER_ROLE_NOT_PARTICIPANT_MSG)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine_no_events(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["items"] == []


@pytest.mark.asyncio
async def test_everything_fine_with_events(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)

    event_one = EventFactory()
    event_two = EventFactory()
    EventFactory()

    EnrollmentFactory(participant=current_user, event=event_one)
    EnrollmentFactory(participant=current_user, event=event_two)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["pages"] == 1
    {item["id"] for item in response_data["items"]} == {event_one.id, event_two.id}
