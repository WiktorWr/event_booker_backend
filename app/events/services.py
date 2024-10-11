from .schemas import CreateEventParams
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.dependencies import get_db
from .models import Event
from app.users.models import User
from app.auth.dependencies import authenticate_user_from_token
from .authorizers import authorize_event_create


@authorize_event_create
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
