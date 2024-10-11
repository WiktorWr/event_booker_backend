from pydantic import BaseModel
from datetime import datetime


class RepresentPayload(BaseModel):
    expires_at: datetime
    sub: str


class RepresentJWT(BaseModel):
    access_token: str
    access_token_expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime


class RevokeTokenParams(BaseModel):
    token: str


class RefreshTokenParams(BaseModel):
    refresh_token: str


class DataFromRefreshToken(BaseModel):
    access_payload: RepresentPayload
    refresh_payload: RepresentPayload
    received_refresh_token: str
