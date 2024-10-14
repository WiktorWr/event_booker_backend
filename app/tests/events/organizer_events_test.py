import pytest
from httpx import AsyncClient
from app.events.exceptions import UserNotOrganizerException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import UserFactory, EventFactory
from fastapi import status

from app.users.enums import UserRole


URL = "/organizer/events"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_not_organizer(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    expected_exception = UserNotOrganizerException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine_no_events(async_client: AsyncClient):
    current_user = UserFactory()
    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_data["items"] == []


@pytest.mark.asyncio
async def test_everything_fine_with_events(async_client: AsyncClient):
    current_user = UserFactory()

    event_one = EventFactory(organizer=current_user)
    event_two = EventFactory(organizer=current_user)
    EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    {item["id"] for item in response_data["items"]} == {event_one.id, event_two.id}
