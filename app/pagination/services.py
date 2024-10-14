from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import Select

from app.pagination.schemas import PaginatedResponse, PaginationParams


def paginate_query[T: BaseModel](
    db: Session, query: Select, pagination: PaginationParams, representer: type[T]
) -> PaginatedResponse[T]:
    paginated_query = query.limit(pagination.per_page).offset(
        (pagination.page - 1) * pagination.per_page
    )

    items = db.scalars(paginated_query)
    represent_items = [representer.model_validate(event) for event in items]

    return PaginatedResponse[T](
        per_page=pagination.per_page,
        page=pagination.page,
        items=represent_items,
    )
