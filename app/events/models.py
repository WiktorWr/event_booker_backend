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
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="event", cascade="all, delete-orphan"
    )


class Enrollment(Base):
    __tablename__ = "enrollments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    participant_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))

    participant: Mapped["User"] = relationship("User", back_populates="enrollments")
    event: Mapped["Event"] = relationship("Event", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint("participant_id", "event_id", name="unique_enrollment"),
    )
