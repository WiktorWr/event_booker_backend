from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class RepresentEvent(BaseModel):
    id: int
    title: str
    price: int | None
    event_date: datetime

    class Config:
        from_attributes = True


class RepresentEventDetails(BaseModel):
    id: int
    title: str
    price: int | None
    event_date: datetime
    description: str
    max_capacity: int | None

    class Config:
        from_attributes = True


class CreateEventParams(BaseModel):
    title: str
    price: int | None = Field(default=None, gt=0)
    event_date: datetime
    description: str
    max_capacity: int | None = Field(default=None, gt=0)


class UpdateEventParams(BaseModel):
    title: Optional[str] = Field(default=None)
    price: Optional[int | None] = Field(default=None, gt=0)
    event_date: Optional[datetime] = Field(default=None)
    description: Optional[str] = Field(default=None)
    max_capacity: Optional[int | None] = Field(default=None, gt=0)


class EventFilters(BaseModel):
    min_price: Optional[int] = Field(default=None)
    max_price: Optional[int] = Field(default=None)
