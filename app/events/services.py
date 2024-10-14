from app.events.filters import get_events_filters
from app.pagination.services import paginate_query
from .schemas import CreateEventParams, EventFilters, UpdateEventParams, RepresentEvent
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.dependencies import get_db
from .models import Event, Enrollment
from app.users.models import User
from app.auth.dependencies import authenticate_user_from_token
from .authorizers import (
    current_user_role_is_organizer,
    event_belongs_to_organizer,
    current_user_role_is_participant,
    participant_is_not_enrolled,
    participant_is_enrolled,
)
from app.pagination.schemas import PaginatedResponse, PaginationParams
from app.pagination.dependencies import pagination_params
from sqlalchemy import select, or_
from .dependencies import get_event_by_id


@current_user_role_is_organizer
def create_event(
    params: CreateEventParams,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> Event:
    event = Event(
        title=params.title,
        description=params.description,
        price=params.price,
        max_capacity=params.max_capacity,
        event_date=params.event_date,
        organizer_id=current_user.id,
    )

    db.add(event)
    db.commit()

    return event


@current_user_role_is_participant
@participant_is_not_enrolled
def enroll_for_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> None:
    enrollment = Enrollment(
        participant_id=current_user.id,
        event_id=event.id,
    )

    db.add(enrollment)
    db.commit()

    return None


@current_user_role_is_organizer
def get_organizer_events(
    *,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> PaginatedResponse[RepresentEvent]:
    query = select(Event).where(Event.organizer_id == current_user.id)

    return paginate_query(db, query, pagination, RepresentEvent, Event.id)


@current_user_role_is_participant
def get_participant_events(
    *,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> PaginatedResponse[RepresentEvent]:
    query = (
        select(Event)
        .join(Enrollment, Enrollment.event_id == Event.id)
        .where(Enrollment.participant_id == current_user.id)
    )

    return paginate_query(db, query, pagination, RepresentEvent, Event.id)


@current_user_role_is_participant
def get_events(
    *,
    filters: EventFilters = Depends(get_events_filters),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> PaginatedResponse[RepresentEvent]:
    query = select(Event)

    if filters.min_price:
        query = query.where(
            or_(Event.price >= filters.min_price, Event.price.is_(None))
        )

    if filters.max_price:
        query = query.where(
            or_(Event.price <= filters.max_price, Event.price.is_(None))
        )

    return paginate_query(db, query, pagination, RepresentEvent, Event.id)


@current_user_role_is_organizer
@event_belongs_to_organizer
def get_organizer_event(
    *,
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> Event:
    return event


@current_user_role_is_organizer
@event_belongs_to_organizer
def update_event(
    params: UpdateEventParams,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> Event:
    update_data = params.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(event, field, value)

    db.commit()
    db.refresh(event)

    return event


@current_user_role_is_participant
def get_event(
    *,
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> Event:
    return event


@current_user_role_is_organizer
@event_belongs_to_organizer
def delete_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> None:
    return db.delete(event)


@current_user_role_is_participant
@participant_is_enrolled
def remove_enrollment(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
):
    enrollment = db.execute(
        select(Enrollment).where(
            Enrollment.event_id == event.id,
            Enrollment.participant_id == current_user.id,
        )
    ).scalar_one()

    return db.delete(enrollment)
