from math import ceil

from app.events.filters import get_events_filters
from .schemas import CreateEventParams, EventFilters, UpdateEventParams, RepresentEvent
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.dependencies import get_db
from .models import Event
from app.users.models import User
from app.auth.dependencies import authenticate_user_from_token
from .authorizers import (
    current_user_role_is_organizer,
    event_belongs_to_organizer,
    current_user_role_is_participant,
)
from app.pagination.schemas import PaginatedResponse, PaginationParams
from app.pagination.dependencies import pagination_params
from app.pagination.enums import SortEnum
from sqlalchemy import desc, asc, select, or_, func
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


@current_user_role_is_organizer
def get_organizer_events(
    *,
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> PaginatedResponse[RepresentEvent]:
    order = desc if pagination.order == SortEnum.DESC else asc

    query = (
        select(Event)
        .where(Event.organizer_id == current_user.id)
        .limit(pagination.per_page)
        .offset(
            pagination.page - 1
            if pagination.page == 1
            else (pagination.page - 1) * pagination.per_page
        )
        .order_by(order(Event.id))
    )

    events = db.scalars(query)
    events_json = [RepresentEvent.model_validate(event) for event in events]
    count = db.execute(
        select(func.count()).select_from(select(Event.id).subquery())
    ).scalar_one()
    pages = ceil(count / pagination.per_page)

    return PaginatedResponse[RepresentEvent](
        pages=pages,
        per_page=pagination.per_page,
        page=pagination.page,
        items=events_json,
    )


@current_user_role_is_participant
def get_events(
    *,
    filters: EventFilters = Depends(get_events_filters),
    pagination: PaginationParams = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
) -> PaginatedResponse[RepresentEvent]:
    order = desc if pagination.order == SortEnum.DESC else asc

    query = (
        select(Event)
        .limit(pagination.per_page)
        .offset(
            pagination.page - 1
            if pagination.page == 1
            else (pagination.page - 1) * pagination.per_page
        )
        .order_by(order(Event.id))
    )

    if filters.min_price:
        query = query.where(
            or_(Event.price >= filters.min_price, Event.price.is_(None))
        )

    if filters.max_price:
        query = query.where(
            or_(Event.price <= filters.max_price, Event.price.is_(None))
        )

    events = db.scalars(query)
    events_json = [RepresentEvent.model_validate(event) for event in events]
    count = db.execute(
        select(func.count()).select_from(select(Event.id).subquery())
    ).scalar_one()
    pages = ceil(count / pagination.per_page)

    return PaginatedResponse[RepresentEvent](
        pages=pages,
        per_page=pagination.per_page,
        page=pagination.page,
        items=events_json,
    )


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


@current_user_role_is_organizer
@event_belongs_to_organizer
def delete_event(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(authenticate_user_from_token),
    event: Event = Depends(get_event_by_id),
) -> None:
    return db.delete(event)
