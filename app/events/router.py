from fastapi import APIRouter, status, Depends
from .schemas import RepresentEventDetails
from .services import create_event, get_organizer_events
from .models import Event
from app.pagination.schemas import PaginatedResponse
from .schemas import RepresentEvent

router = APIRouter(tags=["Event"])


@router.post(
    "/events",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_201_CREATED,
    summary="Create event",
)
async def create(event: Event = Depends(create_event)):
    return event


@router.get(
    "/organizer/events",
    response_model=PaginatedResponse[RepresentEvent],
    status_code=status.HTTP_200_OK,
    summary="Get events",
)
async def organizer_events(
    events: PaginatedResponse[RepresentEvent] = Depends(get_organizer_events),
):
    return events
