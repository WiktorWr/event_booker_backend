from pydantic import BaseModel

from typing import Generic, TypeVar
from .enums import SortEnum

T = TypeVar("T")


class PaginationParams(BaseModel):
    per_page: int
    page: int
    order: SortEnum


class PaginatedResponse(BaseModel, Generic[T]):
    pages: int
    page: int
    per_page: int
    items: list[T]
