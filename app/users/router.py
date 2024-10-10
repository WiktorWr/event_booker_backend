from fastapi import APIRouter, status
from .schemas import UserGetSchema

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "",
    response_model=UserGetSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create user account",
)
async def create():
    return UserGetSchema(id=0)
