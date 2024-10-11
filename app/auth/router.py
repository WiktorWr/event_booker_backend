from fastapi import APIRouter, Depends, status, Response
from .schemas import RepresentJWT
from .services import generate_jtw_data, refresh_token, revoke_token
from .config import settings

router = APIRouter(prefix=settings.AUTH_TOKEN_URL, tags=["Auth"])


@router.post(
    "",
    response_model=RepresentJWT,
    status_code=status.HTTP_201_CREATED,
    summary="Create access and refresh tokens",
)
async def create(jwt_data: RepresentJWT = Depends(generate_jtw_data)):
    return jwt_data


@router.post(
    "/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke access and refresh tokens",
)
async def revoke(_: None = Depends(revoke_token)):
    return Response(status_code=status.HTTP_200_OK)


@router.post(
    "/refresh",
    response_model=RepresentJWT,
    status_code=status.HTTP_201_CREATED,
    summary="Refresh access token",
)
async def refresh(new_jwt_data: RepresentJWT = Depends(refresh_token)):
    return new_jwt_data
