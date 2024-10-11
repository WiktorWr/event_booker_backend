from sqlalchemy.orm import Session
from fastapi import Depends
from app.database.dependencies import get_db
from sqlalchemy import select

from app.exceptions import NotFoundException
from .models import Event


def get_event_by_id(
    event_id: int,
    *,
    db: Session = Depends(get_db),
):
    event: Event | None = db.scalar(select(Event).where(Event.id == event_id))

    if event is None:
        raise NotFoundException(Event.__name__)

    return event
