from decimal import Decimal
from pydantic import BaseModel,ConfigDict,Field,model_validator


class OrderDetailInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    product_id: str=Field(min_length=1,max_length=20)
    quantity: int=Field(strict=True,gt=0,le=2147483647)
    discount: Decimal=Field(default=Decimal(0),ge=0,max_digits=15,decimal_places=2)


class OrderInput(BaseModel):
    model_config=ConfigDict(extra='forbid')
    customer_id: str=Field(min_length=1,max_length=20)
    store_id: str | None=Field(default=None,max_length=20)
    warehouse_id: str | None=Field(default=None,max_length=20)
    details: list[OrderDetailInput]=Field(min_length=1,max_length=200)

    @model_validator(mode='after')
    def unique(self):
        if len({d.product_id for d in self.details})!=len(self.details):
            raise ValueError('Duplicate SKU.')
        return self
