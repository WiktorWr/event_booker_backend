from app.database.model import Base

from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column, Mapped, relationship
from .enums import UserRole
from sqlalchemy.dialects.postgresql import ENUM as PgEnum

from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from app.events.models import Event, Enrollment


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, unique=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(PgEnum(UserRole, name="user_role"))
    events_as_organizer: Mapped[list["Event"]] = relationship(
        back_populates="organizer"
    )
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="participant", cascade="all, delete-orphan"
    )
