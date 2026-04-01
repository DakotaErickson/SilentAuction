import re

import phonenumbers
from pydantic import BaseModel, ConfigDict, field_validator


def is_valid_phone(value: str) -> bool:
    try:
        parsed = phonenumbers.parse(value, "US")
        return phonenumbers.is_valid_number(parsed)
    except phonenumbers.NumberParseException:
        return False

class BidCreate(BaseModel):
    amount: float
    name: str
    contact: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name is required.")
        if len(v.split()) < 2:
            raise ValueError("Please enter both a first and last name.")
        return v

    @field_validator("contact")
    @classmethod
    def validate_contact(cls, v: str) -> str:
        if is_valid_phone(v):
            return v
        raise ValueError("Contact must be a valid phone number.")

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
    name: str
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


class WinnerInfo(BaseModel):
    """The highest bid for an item and the contact who placed it."""
    amount: float
    name: str
    contact: str


class ItemResult(BaseModel):
    """Full results summary for a single auction item."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    starting_bid: float
    final_bid: float
    total_bids: int
    winner: WinnerInfo | None  # None if no bids were placed
    bid_history: list[BidResponse]


class AuctionResults(BaseModel):
    """Top-level admin results payload."""
    total_items: int
    items_with_bids: int
    items_without_bids: int
    results: list[ItemResult]