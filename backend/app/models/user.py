from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import CheckConstraint, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.booking import Booking
    from app.models.review import Review
    from app.models.wishlist import WishlistItem
    from app.models.notification import Notification


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("role IN ('guest', 'host')", name="check_user_role"),
        Index("idx_users_email_unique", "email", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="guest")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_superhost: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)
    updated_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso, onupdate=utc_now_iso)

    # Relationships
    listings: Mapped[List["Listing"]] = relationship("Listing", back_populates="host", cascade="all, delete-orphan")
    bookings: Mapped[List["Booking"]] = relationship("Booking", back_populates="guest")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="author")
    wishlist_items: Mapped[List["WishlistItem"]] = relationship("WishlistItem", back_populates="user", cascade="all, delete-orphan")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
