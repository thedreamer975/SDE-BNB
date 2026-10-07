from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import (
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.user import User


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WishlistItem(Base):
    __tablename__ = "wishlist_items"
    __table_args__ = (
        Index("idx_wishlist_user_created", "user_id", "created_at"),
    )

    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), primary_key=True
    )
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="wishlist_items")
