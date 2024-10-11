from app.database.model import Base

from sqlalchemy import Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.users.models import User


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    max_capacity: Mapped[int] = mapped_column(Integer, nullable=True)
    event_date: Mapped[datetime] = mapped_column(DateTime)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    organizer: Mapped["User"] = relationship(back_populates="events_as_organizer")
