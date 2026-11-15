"""Pydantic schemas.

Input schemas (*Create) carry validation. Output schemas are deliberately
unconstrained so rows saved before validation existed can still be read.
"""

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

VIN_PATTERN = r"^[A-HJ-NPR-Z0-9]{17}$"
MIN_CAR_YEAR = 1900
WorkOrderStatus = Literal["pending", "in_progress", "completed", "cancelled"]


# ---------- Clients ----------

class ClientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    phone: str = Field(min_length=1, max_length=20)
    email: EmailStr

    @field_validator("email")
    @classmethod
    def email_fits_column(cls, value: str) -> str:
        if len(value) > 100:
            raise ValueError("Email must be at most 100 characters")
        return value


class ClientResponse(BaseModel):
    """Flat client: used in lists and create/update responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phone: str
    email: str


# ---------- Cars ----------

class CarCreate(BaseModel):
    client_id: int
    brand: str = Field(min_length=1, max_length=50)
    model: str = Field(min_length=1, max_length=50)
    year: int = Field(ge=MIN_CAR_YEAR)
    vin: str = Field(
        min_length=17,
        max_length=17,
        pattern=VIN_PATTERN,
        description="17 characters: digits and Latin letters except I, O, Q",
    )

    @field_validator("vin", mode="before")
    @classmethod
    def normalize_vin(cls, value):
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("year")
    @classmethod
    def year_not_in_future(cls, value: int) -> int:
        # Checked at request time, so the limit stays right across New Year.
        max_year = datetime.now(timezone.utc).year + 1
        if value > max_year:
            raise ValueError(f"Year must be between {MIN_CAR_YEAR} and {max_year}")
        return value


class CarResponse(BaseModel):
    """Flat car: used in lists and create/update responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    client_id: int
    brand: str
    model: str
    year: int
    vin: str


# ---------- Work orders ----------

class WorkOrderCreate(BaseModel):
    car_id: int
    description: str = Field(min_length=1, max_length=500)
    status: WorkOrderStatus = "pending"


class WorkOrderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    car_id: int
    description: str
    status: str
    created_at: datetime


# ---------- Nested (detail endpoints only) ----------

class CarDetailResponse(CarResponse):
    work_orders: list[WorkOrderResponse] = []


class ClientDetailResponse(ClientResponse):
    cars: list[CarDetailResponse] = []
