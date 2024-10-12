from fastapi import APIRouter, Response, status, Depends
from .schemas import RepresentEventDetails
from .services import create_event, get_organizer_events
from .models import Event
from app.pagination.schemas import PaginatedResponse
from .schemas import RepresentEvent
from .services import (
    get_organizer_event,
    update_event,
    delete_event,
    get_events,
    get_event,
)

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
    "/events",
    response_model=PaginatedResponse[RepresentEvent],
    status_code=status.HTTP_200_OK,
    summary="List of events",
)
async def get_all_events(
    events: PaginatedResponse[RepresentEvent] = Depends(get_events),
):
    return events


@router.get(
    "/events/{event_id}",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_200_OK,
    summary="Get event details",
)
async def event_details(
    event: Event = Depends(get_event),
):
    return event


@router.patch(
    "/organizer/events/{event_id}",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_200_OK,
    summary="Update event's data",
)
async def update(
    updated_event: Event = Depends(update_event),
):
    return updated_event


@router.delete(
    "/organizer/events/{event_id}",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_200_OK,
    summary="Delete event",
)
async def delete(
    _: None = Depends(delete_event),
):
    return Response(status_code=status.HTTP_200_OK)


@router.get(
    "/organizer/events",
    response_model=PaginatedResponse[RepresentEvent],
    status_code=status.HTTP_200_OK,
    summary="Get organizer's events",
)
async def organizer_events(
    events: PaginatedResponse[RepresentEvent] = Depends(get_organizer_events),
):
    return events


@router.get(
    "/organizer/events/{event_id}",
    response_model=RepresentEventDetails,
    status_code=status.HTTP_200_OK,
    summary="Get organizer's event details",
)
async def organizer_event_details(
    event: Event = Depends(get_organizer_event),
):
    return event
