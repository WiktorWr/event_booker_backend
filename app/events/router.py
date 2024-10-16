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
    enroll_for_event,
    get_participant_events,
    remove_enrollment,
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


@router.post(
    "/events/{event_id}/enroll",
    status_code=status.HTTP_201_CREATED,
    summary="Enroll for the event",
)
async def enroll(
    _: None = Depends(enroll_for_event),
):
    return Response(status_code=status.HTTP_201_CREATED)


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
    "/participant/events",
    response_model=PaginatedResponse[RepresentEvent],
    status_code=status.HTTP_200_OK,
    summary="Get participant's events",
)
async def participant_events(
    events: PaginatedResponse[RepresentEvent] = Depends(get_participant_events),
):
    return events


@router.delete(
    "/participant/events/{event_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel participant's enrollment",
)
async def cancel_enrollment(
    _: None = Depends(remove_enrollment),
):
    return Response(status_code=status.HTTP_200_OK)


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
