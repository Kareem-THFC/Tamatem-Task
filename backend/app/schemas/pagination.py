"""Validation schema shared by the paginated list endpoints."""

from typing import Annotated

from pydantic import BaseModel, Field

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


class PaginationQuery(BaseModel):
    """The ``?page=`` and ``?page_size=`` parameters every list endpoint takes.
    """

    page: Annotated[int, Field(ge=1)] = 1
    page_size: Annotated[int, Field(ge=1, le=MAX_PAGE_SIZE)] = DEFAULT_PAGE_SIZE
