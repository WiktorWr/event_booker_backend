from app.database.model import Base

from sqlalchemy import Integer, String, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
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
    event_enrollments: Mapped["Enrollment"] = relationship(back_populates="event")
    participants: Mapped[list["User"]] = relationship(
        secondary="enrollments", back_populates="events_as_participant"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    participant_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", primary_key=True)
    )
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), primary_key=True)

    event: Mapped["Event"] = relationship(back_populates="event_enrollments")
    participant: Mapped["User"] = relationship(back_populates="participant_enrollments")

    __table_args__ = (
        UniqueConstraint("participant_id", "event_id", name="unique_participant_event"),
    )
