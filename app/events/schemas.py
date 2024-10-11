from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


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
    price: Optional[int] = Field(default=None, gt=0)
    event_date: datetime
    description: str
    max_capacity: Optional[int] = Field(default=None, gt=0)
