import pytest
from httpx import AsyncClient
from app.tests.factories import RevokedTokenFactory
from app.auth.router import router as auth_router
from fastapi import status
from sqlalchemy.orm import Session
from app.auth.models import RevokedToken
from sqlalchemy import select, func

REVOKE_URL = f"{auth_router.prefix}/revoke"


@pytest.mark.asyncio
async def test_missing_params(async_client: AsyncClient):
    response = await async_client.post(REVOKE_URL, json={})
    response_data = response.json()
    errors = response_data["detail"]

    expected_missing_fields = {"token"}

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    for field in expected_missing_fields:
        assert any(
            error["loc"][-1] == field for error in errors
        ), f"Missing validation error for field: {field}"


@pytest.mark.asyncio
async def test_revoke_already_revoked_token(
    db_session: Session, async_client: AsyncClient
):
    revoked_token = RevokedTokenFactory()

    json_data = {"token": revoked_token.hash}

    assert (
        db_session.scalar(
            select(func.count())
            .select_from(RevokedToken)
            .where(RevokedToken.hash == json_data["token"])
        )
        == 1
    )

    response = await async_client.post(REVOKE_URL, json=json_data)

    assert response.status_code == status.HTTP_200_OK
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(RevokedToken)
            .where(RevokedToken.hash == json_data["token"])
        )
        == 1
    )


@pytest.mark.asyncio
async def test_revoke_token(db_session: Session, async_client: AsyncClient):
    json_data = {"token": "hash"}

    assert db_session.scalar(select(func.count()).select_from(RevokedToken)) == 0

    response = await async_client.post(REVOKE_URL, json=json_data)

    assert response.status_code == status.HTTP_200_OK
    assert (
        db_session.scalar(
            select(func.count())
            .select_from(RevokedToken)
            .where(RevokedToken.hash == json_data["token"])
        )
        == 1
    )
