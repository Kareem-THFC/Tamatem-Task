"""Validation schema for purchase requests."""

from typing import Annotated

from pydantic import BaseModel, Field


class CreateOrderRequest(BaseModel):
    """The JSON payload accepted by ``POST /api/orders``.
    """

    product_id: Annotated[int, Field(strict=True, gt=0)]
