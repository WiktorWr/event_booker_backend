import pytest
from httpx import AsyncClient
from app.events.exceptions import (
    EventNotBelongToUserException,
    UserNotOrganizerException,
)
from app.events.models import Event
from app.exceptions import NotFoundException
from app.tests import utils
from app.auth.exceptions import InvalidTokenException
from app.tests.factories import EventFactory, UserFactory
from fastapi import status
from app.users.enums import UserRole
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime


BASE_URL = "/organizer/events"


def url(event_id: int) -> str:
    return f"{BASE_URL}/{event_id}"


@pytest.mark.asyncio
async def test_user_unauthorized(async_client: AsyncClient):
    headers = utils.auth_header("invalid")

    response = await async_client.patch(url(1), headers=headers)
    response_data = response.json()

    expected_exception = InvalidTokenException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_event_not_found(async_client: AsyncClient):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.patch(url(event.id + 1), headers=headers)
    response_data = response.json()

    expected_exception = NotFoundException(Event.__name__)

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_user_is_not_organizer(async_client: AsyncClient):
    current_user = UserFactory(role=UserRole.PARTICIPANT)
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.patch(url(event.id), headers=headers, json={})

    response_data = response.json()
    expected_exception = UserNotOrganizerException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_current_user_not_event_owner(async_client: AsyncClient):
    current_user = UserFactory()
    other_user = UserFactory()
    event = EventFactory(organizer=other_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.patch(url(event.id), headers=headers, json={})
    response_data = response.json()

    expected_exception = EventNotBelongToUserException()

    assert response.status_code == expected_exception.status_code
    assert response_data["detail"] == expected_exception.detail


@pytest.mark.asyncio
async def test_everything_fine_no_params(
    db_session: Session, async_client: AsyncClient
):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    response = await async_client.patch(url(event.id), headers=headers, json={})

    updated_event = db_session.execute(
        select(Event).where(Event.id == event.id)
    ).scalar_one()

    assert response.status_code == status.HTTP_200_OK
    assert event.title == updated_event.title
    assert event.price == updated_event.price
    assert event.event_date == updated_event.event_date
    assert event.description == updated_event.description
    assert event.max_capacity == updated_event.max_capacity


@pytest.mark.asyncio
async def test_everything_fine_all_params(
    db_session: Session, async_client: AsyncClient
):
    current_user = UserFactory()
    event = EventFactory(organizer=current_user)

    headers = utils.generate_user_auth_header(current_user.id)

    new_date_time = datetime.now()

    json_data = {
        "title": "New title",
        "price": 200_000_00,
        "event_date": str(new_date_time),
        "description": "New description",
        "max_capacity": 200,
    }

    response = await async_client.patch(url(event.id), headers=headers, json=json_data)

    updated_event = db_session.execute(
        select(Event).where(Event.id == event.id)
    ).scalar_one()

    assert response.status_code == status.HTTP_200_OK
    assert updated_event.title == json_data["title"]
    assert updated_event.price == json_data["price"]
    assert updated_event.event_date == new_date_time
    assert updated_event.description == json_data["description"]
    assert updated_event.max_capacity == json_data["max_capacity"]
