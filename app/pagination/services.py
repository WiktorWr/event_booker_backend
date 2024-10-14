from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Select, asc, desc

from app.pagination.enums import SortEnum
from app.pagination.schemas import PaginatedResponse, PaginationParams
from sqlalchemy.orm.attributes import InstrumentedAttribute


def paginate_query[T: BaseModel](
    db: Session,
    query: Select,
    pagination: PaginationParams,
    representer: type[T],
    order_by_column: InstrumentedAttribute,
) -> PaginatedResponse[T]:
    order = (
        asc(order_by_column)
        if pagination.order == SortEnum.ASC
        else desc(order_by_column)
    )

    paginated_query = (
        query.order_by(order)
        .limit(pagination.per_page)
        .offset((pagination.page - 1) * pagination.per_page)
    )

    items = db.scalars(paginated_query)
    represent_items = [representer.model_validate(event) for event in items]

    return PaginatedResponse[T](
        per_page=pagination.per_page,
        page=pagination.page,
        items=represent_items,
    )
