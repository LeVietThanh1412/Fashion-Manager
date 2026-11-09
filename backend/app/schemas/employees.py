from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field


class EmployeeInput(BaseModel):
    model_config = ConfigDict(extra='forbid',str_strip_whitespace=True)
    employee_id: str = Field(min_length=1,max_length=20)
    name: str = Field(min_length=1,max_length=255)
    phone: str = Field(min_length=1,max_length=25)
    email: str = Field(min_length=1,max_length=255)
    store_id: str = Field(min_length=1,max_length=20)
    position_id: str = Field(min_length=1,max_length=30)
    salary: Decimal = Field(gt=0,max_digits=15,decimal_places=2)


class SalaryInput(BaseModel):
    salary: Decimal = Field(gt=0,max_digits=15,decimal_places=2)


class StatusInput(BaseModel):
    status: Literal['active','inactive']


class WorkInput(BaseModel):
    store_id: str = Field(min_length=1,max_length=20)
