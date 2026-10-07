"""
Pydantic schemas for the Host API (listings CRUD, reservations, dashboard).
"""
from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


VALID_ROOM_TYPES = {"entire_home", "private_room", "shared_room"}


class PhotoInput(BaseModel):
    url: str
    position: int
    alt: Optional[str] = None

    @field_validator("url")
    @classmethod
    def url_must_be_https(cls, v: str) -> str:
        if not v.startswith(("https://", "http://localhost", "http://127.0.0.1")):
            raise ValueError("Photo URL must use HTTPS")
        if len(v) > 1000:
            raise ValueError("URL too long (max 1000 chars)")
        return v


class CreateListingRequest(BaseModel):
    title: str
    description: str
    category: str
    property_type: str
    room_type: str
    address: Optional[str] = None
    city: str
    state: Optional[str] = None
    country: str
    latitude: float
    longitude: float
    max_guests: int
    bedrooms: int
    beds: int
    baths: float
    pets_allowed: bool = False
    photos: list[PhotoInput]
    amenity_ids: list[int]
    price_per_night: int   # cents
    cleaning_fee: int = 0  # cents
    min_nights: int = 1
    max_nights: int = 30
    check_in_time: str = "15:00"
    check_out_time: str = "11:00"
    house_rules: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        v = v.strip()
        if not (5 <= len(v) <= 255):
            raise ValueError("Title must be 5–255 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str) -> str:
        v = v.strip()
        if not (20 <= len(v) <= 5000):
            raise ValueError("Description must be 20–5000 characters")
        return v

    @field_validator("room_type")
    @classmethod
    def valid_room_type(cls, v: str) -> str:
        if v not in VALID_ROOM_TYPES:
            raise ValueError(f"room_type must be one of {sorted(VALID_ROOM_TYPES)}")
        return v

    @field_validator("max_guests")
    @classmethod
    def guests_range(cls, v: int) -> int:
        if not 1 <= v <= 16:
            raise ValueError("max_guests must be 1–16")
        return v

    @field_validator("price_per_night")
    @classmethod
    def price_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("price_per_night must be > 0")
        return v

    @field_validator("cleaning_fee")
    @classmethod
    def cleaning_non_negative(cls, v: int) -> int:
        if v < 0:
            raise ValueError("cleaning_fee must be >= 0")
        return v

    @field_validator("photos")
    @classmethod
    def photos_count(cls, v: list) -> list:
        if not 1 <= len(v) <= 10:
            raise ValueError("Must provide 1–10 photos")
        return v

    @model_validator(mode="after")
    def min_lte_max_nights(self) -> "CreateListingRequest":
        if self.min_nights > self.max_nights:
            raise ValueError("min_nights must be <= max_nights")
        return self


class UpdateListingRequest(BaseModel):
    """All fields optional for PATCH/PUT."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    property_type: Optional[str] = None
    room_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    max_guests: Optional[int] = None
    bedrooms: Optional[int] = None
    beds: Optional[int] = None
    baths: Optional[float] = None
    pets_allowed: Optional[bool] = None
    photos: Optional[list[PhotoInput]] = None
    amenity_ids: Optional[list[int]] = None
    price_per_night: Optional[int] = None
    cleaning_fee: Optional[int] = None
    min_nights: Optional[int] = None
    max_nights: Optional[int] = None
    check_in_time: Optional[str] = None
    check_out_time: Optional[str] = None
    house_rules: Optional[str] = None


class HostListingResponse(BaseModel):
    id: str
    title: str
    city: str
    country: str
    price_per_night: int
    rating_avg: float
    rating_count: int
    photos: list[str]
    upcoming_bookings: int
    is_active: bool


class HostDashboardResponse(BaseModel):
    checking_out: int
    currently_hosting: int
    arriving_soon: int
    upcoming: int
    total_listings: int
    upcoming_bookings: int
    revenue_30d: int
    avg_rating: float


class UploadResponse(BaseModel):
    url: str
    filename: str
