from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base
from app.models.amenity import listing_amenities

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.amenity import Amenity
    from app.models.booking import Booking
    from app.models.review import Review
    from app.models.wishlist import WishlistItem


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ListingPhoto(Base):
    __tablename__ = "listing_photos"
    __table_args__ = (
        UniqueConstraint("listing_id", "position", name="uq_listing_photo_position"),
        Index("idx_listing_photos_position", "listing_id", "position"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(1000), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    alt: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationship
    listing: Mapped["Listing"] = relationship("Listing", back_populates="photos")


class Listing(Base):
    __tablename__ = "listings"
    __table_args__ = (
        CheckConstraint(
            "room_type IN ('entire_home', 'private_room', 'shared_room')",
            name="check_listing_room_type",
        ),
        CheckConstraint("price_cents > 0", name="check_listing_price_positive"),
        CheckConstraint("cleaning_fee_cents >= 0", name="check_listing_cleaning_non_negative"),
        CheckConstraint("max_guests >= 1 AND max_guests <= 16", name="check_listing_max_guests"),
        CheckConstraint("min_nights >= 1", name="check_listing_min_nights"),
        CheckConstraint("max_nights >= min_nights", name="check_listing_max_nights_gte_min"),
        Index("idx_listings_deleted_id", "deleted_at", "id"),
        Index("idx_listings_city", "city"),
        Index("idx_listings_country", "country"),
        Index("idx_listings_category", "category"),
        Index("idx_listings_host_id", "host_id"),
        Index("idx_listings_price_cents", "price_cents"),
        Index("idx_listings_room_type", "room_type"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    host_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    property_type: Mapped[str] = mapped_column(String(50), nullable=False)
    room_type: Mapped[str] = mapped_column(String(30), nullable=False)
    address_line: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaning_fee_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_guests: Mapped[int] = mapped_column(Integer, nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    beds: Mapped[int] = mapped_column(Integer, nullable=False)
    baths: Mapped[float] = mapped_column(Float, nullable=False)
    pets_allowed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    check_in_time: Mapped[str] = mapped_column(String(10), nullable=False, default="15:00")
    check_out_time: Mapped[str] = mapped_column(String(10), nullable=False, default="11:00")
    min_nights: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    max_nights: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    house_rules: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    rating_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    rating_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deleted_at: Mapped[Optional[str]] = mapped_column(String(35), nullable=True)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(
        String(35), nullable=False, default=utc_now_iso, onupdate=utc_now_iso
    )

    # Relationships
    host: Mapped["User"] = relationship("User", back_populates="listings")
    photos: Mapped[List[ListingPhoto]] = relationship(
        "ListingPhoto",
        back_populates="listing",
        cascade="all, delete-orphan",
        order_by="ListingPhoto.position",
    )
    amenities: Mapped[List["Amenity"]] = relationship(
        "Amenity",
        secondary=listing_amenities,
        back_populates="listings",
    )
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="listing")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="listing")
    wishlist_items: Mapped[List["WishlistItem"]] = relationship(
        "WishlistItem", back_populates="listing", cascade="all, delete-orphan"
    )
