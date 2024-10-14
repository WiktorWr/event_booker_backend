import pytest
from httpx import AsyncClient
from app.events.exceptions import UserNotParticipantException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import EventFactory, UserFactory
from app.users.enums import UserRole
from fastapi import status

URL = "/events"


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

    expected_exception = UserNotParticipantException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine_not_filters(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)

    event_one = EventFactory()
    event_two = EventFactory()
    event_three = EventFactory()

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.get(URL, headers=headers)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    {item["id"] for item in response_data["items"]} == {
        event_one.id,
        event_two.id,
        event_three.id,
    }


@pytest.mark.asyncio
async def test_everything_fine_with_min_price_filter(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)

    event_one = EventFactory(price=100)  # noqa
    event_two = EventFactory(price=200)
    event_three = EventFactory(price=300)
    event_four = EventFactory(price=None)

    headers = utils.generate_user_auth_header(current_user.id)

    params = {"min_price": 200}

    response = await async_client.get(URL, headers=headers, params=params)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    {item["id"] for item in response_data["items"]} == {
        event_two.id,
        event_three.id,
        event_four.id,
    }


@pytest.mark.asyncio
async def test_everything_fine_with_max_price_filter(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)

    event_one = EventFactory(price=100)
    event_two = EventFactory(price=200)
    event_three = EventFactory(price=300)  # noqa
    event_four = EventFactory(price=None)

    headers = utils.generate_user_auth_header(current_user.id)

    params = {"max_price": 200}

    response = await async_client.get(URL, headers=headers, params=params)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    {item["id"] for item in response_data["items"]} == {
        event_one.id,
        event_two.id,
        event_four.id,
    }


@pytest.mark.asyncio
async def test_everything_fine_with_all_filters(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)

    event_one = EventFactory(price=100)  # noqa
    event_two = EventFactory(price=200)
    event_three = EventFactory(price=300)  # noqa
    event_four = EventFactory(price=None)

    headers = utils.generate_user_auth_header(current_user.id)

    params = {"min_price": 150, "max_price": 200}

    response = await async_client.get(URL, headers=headers, params=params)
    response_data = response.json()

    assert response.status_code == status.HTTP_200_OK
    {item["id"] for item in response_data["items"]} == {event_two.id, event_four.id}
