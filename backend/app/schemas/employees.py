from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class EmployeeInput(BaseModel):
    employee_id: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=1, max_length=25)
    email: str = Field(min_length=1, max_length=255)
    role: Literal["regional_manager", "store_manager", "staff"]
    store_id: str | None = Field(default=None, max_length=20)
    region_id: int | None = Field(default=None, ge=1, le=3)
    # The active database uses DECIMAL(15, 0) NOT NULL CHECK (luong > 0).
    # Keep None here so the route can return a clear validation error after
    # checking the caller's scope instead of sending an invalid INSERT to MySQL.
    salary: Decimal | None = Field(default=None, gt=0, max_digits=15, decimal_places=0)


class SalaryInput(BaseModel):
    salary: Decimal = Field(gt=0, max_digits=15, decimal_places=0)


class StatusInput(BaseModel):
    status: Literal["active", "inactive"]


class RoleDemotionInput(BaseModel):
    store_id: str | None = Field(default=None, max_length=20)
