from fastapi import APIRouter, status, Depends
from .schemas import RepresentEventDetails
from .services import create_event
from .models import Event

router = APIRouter(tags=["Event"])


@router.post(
    "/events",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
)
async def create(event: Event = Depends(create_event)):
    return event
