from .schemas import SortEnum, PaginationParams


def pagination_params(
    page: int = 1, per_page: int = 10, order: SortEnum = SortEnum.DESC
):
    return PaginationParams(page=page, per_page=per_page, order=order.value)
