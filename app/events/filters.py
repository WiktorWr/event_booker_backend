from .schemas import EventFilters
from typing import Optional


def get_events_filters(
    min_price: Optional[int] = None, max_price: Optional[int] = None
):
    return EventFilters(min_price=min_price, max_price=max_price)
