import re

import phonenumbers
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


def is_valid_phone(value: str) -> bool:
    try:
        parsed = phonenumbers.parse(value, "US")
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False


def is_valid_email(value: str) -> bool:
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value))


class BidCreate(BaseModel):
    amount: float
    contact: str

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: str) -> str:
        if is_valid_email(v) or is_valid_phone(v):
            return v
        raise ValueError("Contact must be a valid email address or US phone number.")

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Bid amount must be positive.")
        return round(v, 2)


class BidResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    item_id: int
    amount: float
    contact: str


class ItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    starting_bid: float
    current_bid: float
    image_url: str | None
    bids: list[BidResponse] = []


class BidResult(BaseModel):
    """Returned after a successful bid, also used as WebSocket broadcast payload."""
    item_id: int
    item_name: str
    current_bid: float
    bid_id: int