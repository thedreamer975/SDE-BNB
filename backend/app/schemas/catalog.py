from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.meta import AmenityItem


class DestinationSuggestion(BaseModel):
    label: str
    city: str | None = None
    country: str | None = None
    lat: float | None = None
    lng: float | None = None


class PhotoItem(BaseModel):
    id: int
    url: str
    position: int
    alt: str | None = None

    model_config = ConfigDict(from_attributes=True)


class HostSummary(BaseModel):
    id: int
    name: str
    avatar_url: str | None = None
    is_superhost: bool = False
    joined_year: int
    listing_count: int


class ListingCardResponse(BaseModel):
    id: int
    title: str
    category: str
    property_type: str
    room_type: str
    city: str
    country: str
    latitude: float
    longitude: float
    price_cents: int
    cleaning_fee_cents: int
    max_guests: int
    bedrooms: int
    beds: int
    baths: float
    pets_allowed: bool
    rating_avg: float
    rating_count: int
    is_superhost: bool = False
    guest_favorite: bool = False
    photos: list[PhotoItem]
    saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class ListingDetailResponse(BaseModel):
    id: int
    title: str
    description: str
    category: str
    property_type: str
    room_type: str
    address_line: str
    city: str
    country: str
    latitude: float
    longitude: float
    price_cents: int
    cleaning_fee_cents: int
    max_guests: int
    bedrooms: int
    beds: int
    baths: float
    pets_allowed: bool
    check_in_time: str
    check_out_time: str
    min_nights: int
    max_nights: int
    house_rules: str | None = None
    rating_avg: float
    rating_count: int
    guest_favorite: bool = False
    host: HostSummary
    photos: list[PhotoItem]
    amenities: list[AmenityItem]
    saved: bool = False

    model_config = ConfigDict(from_attributes=True)


class ListingListResponse(BaseModel):
    items: list[ListingCardResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class ListingCountResponse(BaseModel):
    total: int


class HistogramBucket(BaseModel):
    from_cents: int = Field(..., serialization_alias="from")
    to_cents: int = Field(..., serialization_alias="to")
    count: int

    model_config = ConfigDict(populate_by_name=True)


class ListingFacetsResponse(BaseModel):
    price_min: int
    price_max: int
    histogram: list[HistogramBucket]


class ReviewAuthor(BaseModel):
    id: int
    name: str
    avatar_url: str | None = None


class ReviewItem(BaseModel):
    id: int
    author: ReviewAuthor
    cleanliness: int
    accuracy: int
    communication: int
    location: int
    check_in_rating: int
    value: int
    rating: float
    comment: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReviewsSummary(BaseModel):
    avg: float
    count: int
    categories: dict[str, float]


class ReviewsListResponse(BaseModel):
    items: list[ReviewItem]
    summary: ReviewsSummary
    total: int
    has_more: bool


class BookedRange(BaseModel):
    check_in: str
    check_out: str


class AvailabilityResponse(BaseModel):
    booked: list[BookedRange]
    min_nights: int
    max_nights: int
    max_advance_days: int
