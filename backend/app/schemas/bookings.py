"""
Pydantic schemas for booking and host reservation endpoints.
"""
from typing import Optional
from pydantic import BaseModel, field_validator


class QuoteParams(BaseModel):
    listing_id: Optional[str] = None
    check_in: str
    check_out: str
    adults: int = 1
    children: int = 0
    infants: int = 0
    pets: int = 0


class QuoteResponse(BaseModel):
    listing_id: str
    check_in: str
    check_out: str
    nights: int
    price_per_night: int
    nightly_total: int
    cleaning_fee: int
    service_fee: int
    total: int
    currency: str = "USD"


class CreateBookingRequest(BaseModel):
    listing_id: str | int
    check_in: str
    check_out: str
    adults: int
    children: int = 0
    infants: int = 0
    pets: int = 0
    card_token: Optional[str] = None
    payment_token: Optional[str] = None

    @field_validator("adults")
    @classmethod
    def adults_at_least_one(cls, v: int) -> int:
        if v < 1:
            raise ValueError("At least 1 adult required")
        return v


class BookingResponse(BaseModel):
    id: str
    listing_id: str
    listing_title: str
    listing_city: str
    listing_country: str
    listing_photo: Optional[str]
    check_in: str
    check_out: str
    adults: int
    children: int
    infants: int
    pets: int
    nights: int
    price_per_night: int
    nightly_total: int
    cleaning_fee: int
    service_fee: int
    total_price: int
    status: str
    payment_status: str
    refund_amount: int
    confirmation_code: str
    phase: str
    can_cancel: bool
    can_review: bool
    has_review: bool
    created_at: str
    cancelled_at: Optional[str]


class CancelPreviewResponse(BaseModel):
    booking_id: str
    refund_amount: int
    refund_policy: str
    nights_elapsed: int
    nights_total: int


class CreateReviewRequest(BaseModel):
    rating: int
    comment: str

    @field_validator("rating")
    @classmethod
    def rating_in_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be 1–5")
        return v

    @field_validator("comment")
    @classmethod
    def comment_length(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 10:
            raise ValueError("Comment must be at least 10 characters")
        if len(stripped) > 1000:
            raise ValueError("Comment must be at most 1000 characters")
        return stripped
