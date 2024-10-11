from fastapi import APIRouter, status, Depends
from .schemas import RepresentUser
from .services import create_user
from .models import User

router = APIRouter(prefix="/users", tags=["User"])


@router.post(
    "",
    response_model=RepresentUser,
    status_code=status.HTTP_201_CREATED,
    summary="Create user account",
)
async def create(user: User = Depends(create_user)):
    return user
