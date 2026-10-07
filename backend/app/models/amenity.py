from datetime import datetime, timezone
from typing import TYPE_CHECKING, List
from sqlalchemy import Column, ForeignKey, Index, Integer, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.listing import Listing


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# Composite PK join table between listings and amenities
listing_amenities = Table(
    "listing_amenities",
    Base.metadata,
    Column("listing_id", Integer, ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True),
    Column("amenity_id", Integer, ForeignKey("amenities.id", ondelete="CASCADE"), primary_key=True),
    Index("idx_listing_amenities_amenity_id", "amenity_id"),
)


class Amenity(Base):
    __tablename__ = "amenities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    icon_key: Mapped[str] = mapped_column(String(50), nullable=False)
    group: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationship
    listings: Mapped[List["Listing"]] = relationship(
        "Listing",
        secondary=listing_amenities,
        back_populates="amenities",
    )
