from pydantic import BaseModel, Field


class OrderDetailInput(BaseModel):
    product_id: str = Field(min_length=1, max_length=20)
    quantity: int = Field(gt=0)


class OrderInput(BaseModel):
    customer_id: str = Field(min_length=1, max_length=20)
    details: list[OrderDetailInput] = Field(min_length=1)
