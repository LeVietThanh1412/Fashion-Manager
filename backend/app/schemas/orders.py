from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class OrderDetailInput(BaseModel):
    detail_id: str = Field(min_length=1, max_length=20)
    product_id: str = Field(min_length=1, max_length=20)
    quantity: int = Field(gt=0)
    unit_price: Decimal = Field(ge=0)


class OrderInput(BaseModel):
    order_id: str = Field(min_length=1, max_length=20)
    employee_id: str = Field(min_length=1, max_length=20)
    customer_id: str = Field(min_length=1, max_length=20)
    created_at: datetime
    details: list[OrderDetailInput] = Field(min_length=1)
