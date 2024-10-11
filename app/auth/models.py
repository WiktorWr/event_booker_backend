from datetime import datetime

from app.database.model import Base

from sqlalchemy import Integer, DateTime, String
from sqlalchemy.orm import mapped_column, Mapped


class RevokedToken(Base):
    __tablename__ = "revoked_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String, nullable=False, index=True, unique=True)
    revoked_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(), nullable=False
    )
