import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from app.users.models import User
from app.tests.factories import UserFactory
from app.users.router import router as users_router
from fastapi import status
from sqlalchemy import select, func


@pytest.mark.asyncio
async def test_one(async_client: AsyncClient):
    response = await async_client.post(users_router.prefix, json={})

    assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.asyncio
async def test_two(db_session: Session):
    UserFactory()

    assert db_session.scalar(select(func.count()).select_from(User)) == 1
