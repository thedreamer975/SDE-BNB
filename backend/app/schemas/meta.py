from pydantic import BaseModel


class AmenityItem(BaseModel):
    id: int
    name: str
    icon_key: str
    group: str


class MetaLimits(BaseModel):
    max_guests: int = 16
    max_bedrooms: int = 20
    max_beds: int = 30
    max_baths: float = 20.0
    min_nightly_cents: int = 1000  # $10.00
    min_nights: int = 1
    max_nights: int = 365
    max_advance_days: int = 365


class MetaResponse(BaseModel):
    today: str
    categories: list[str]
    property_types: list[str]
    room_types: list[str]
    amenities: list[AmenityItem]
    limits: MetaLimits
