from fastapi import Depends

from .schemas import (
    RepresentJWT,
    RepresentPayload,
    DataFromRefreshToken,
    RevokeTokenParams,
)
from .dependencies import get_user_id_from_credentials
from .models import RevokedToken
from .config import settings
from datetime import datetime, timedelta
from jose import jwt
from .validators import validate_token_revoke

from sqlalchemy.orm import Session
from app.database.dependencies import get_db

from .dependencies import get_payload_from_refresh_token


def generate_jtw_data(
    *, user_id: int = Depends(get_user_id_from_credentials)
) -> RepresentJWT:
    ### HELPER FUNCTIONS ###
    def _create_payload(subject: int | str, timedelta_minutes: int) -> RepresentPayload:
        expires_at = datetime.now() + timedelta(minutes=timedelta_minutes)
        payload = {"expires_at": expires_at, "sub": str(subject)}
        return RepresentPayload(**payload)

    def _encode_payload(payload: RepresentPayload, key: str) -> str:
        return jwt.encode(
            {"expires_at": str(payload.expires_at.timestamp()), "sub": payload.sub},
            key,
            algorithm=settings.ALGORITHM,
        )

    ### MAIN LOGIC ###
    access_payload = _create_payload(user_id, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = _encode_payload(access_payload, settings.JWT_SECRET_KEY)
    refresh_payload = _create_payload(
        access_token, settings.REFRESH_TOKEN_EXPIRE_MINUTES
    )
    refresh_token = _encode_payload(refresh_payload, settings.JWT_REFRESH_SECRET_KEY)
    return RepresentJWT(
        access_token=access_token,
        access_token_expires_at=access_payload.expires_at,
        refresh_token=refresh_token,
        refresh_token_expires_at=refresh_payload.expires_at,
    )


def refresh_token(
    *,
    db: Session = Depends(get_db),
    data_from_refresh_token: DataFromRefreshToken = Depends(
        get_payload_from_refresh_token
    ),
) -> RepresentJWT:
    ### HELPER FUNCTIONS ###
    def _revoke(token: str) -> None:
        return revoke_token(RevokeTokenParams(token=token), db=db, commit_session=False)

    ### MAIN LOGIC ###
    _revoke(data_from_refresh_token.refresh_payload.sub)  # revokes old access token
    _revoke(
        data_from_refresh_token.received_refresh_token
    )  # revokes used refresh token
    new_tokens = generate_jtw_data(
        user_id=int(data_from_refresh_token.access_payload.sub)
    )
    db.commit()
    return new_tokens


@validate_token_revoke
def revoke_token(
    params: RevokeTokenParams,
    *,
    db: Session = Depends(get_db),
    commit_session: bool = True,
) -> None:
    revoked_token = RevokedToken(hash=params.token)
    db.add(revoked_token)
    if commit_session:
        db.commit()
    return None
