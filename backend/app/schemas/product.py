"""Validation schemas for product CSV rows and product query parameters."""

from decimal import Decimal
from enum import Enum
from typing import Annotated

from pydantic import BaseModel, Field, StringConstraints, field_validator

from app.schemas.pagination import PaginationQuery


class ProductRow(BaseModel):
    """One row of the products CSV, after validation and normalization.

    Unlike the API request schemas, this model deliberately allows Pydantic's
    default coercion: every CSV value arrives as a string, so ``"20.5"`` must
    be accepted and converted to ``Decimal("20.5")``. A JSON client can send
    real types, which is why ``LoginRequest`` uses ``strict=True`` instead.
    """

    id: Annotated[int, Field(gt=0)]

    title: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1, max_length=255),
    ]

    description: Annotated[
        str,
        StringConstraints(strip_whitespace=True, min_length=1),
    ]

    # max_digits and decimal_places mirror the Numeric(10, 2) price column, so
    # a value the database could not store faithfully is reported as an invalid
    # row instead of being silently rounded.
    price: Annotated[Decimal, Field(ge=0, max_digits=10, decimal_places=2)]

    # Locations are upper-cased so the ?location= filter can compare exactly,
    # regardless of how the CSV happens to be capitalised.
    location: Annotated[
        str,
        StringConstraints(
            strip_whitespace=True, to_upper=True, min_length=1, max_length=10
        ),
    ]


LocationFilter = Annotated[
    str,
    StringConstraints(strip_whitespace=True, to_upper=True, max_length=10),
]

# A search box can hold a lot of text. The cap is generous for a real query but
# stops an enormous string being turned into a LIKE pattern.
MAX_SEARCH_LENGTH = 100

SearchFilter = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=MAX_SEARCH_LENGTH),
]


class ProductSort(str, Enum):
    """The orderings ``GET /api/products`` accepts.
    """

    NEWEST = "default"
    PRICE_ASC = "price_asc"
    PRICE_DESC = "price_desc"


class ProductListQuery(PaginationQuery):
    """The query string accepted by ``GET /api/products``.
    """

    location: LocationFilter | None = None

    #: Free text matched against the title and description.
    search: SearchFilter | None = None

    sort: ProductSort = ProductSort.NEWEST

    @field_validator("location", "search")
    @classmethod
    def _treat_blank_as_absent(cls, value: str | None) -> str | None:
        """Let ``?location=`` and ``?search=`` mean "no filter".
        """
        return value or None
