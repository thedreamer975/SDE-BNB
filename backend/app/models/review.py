from datetime import datetime, timezone
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.listing import Listing
    from app.models.booking import Booking
    from app.models.user import User


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint(
            "cleanliness >= 1 AND cleanliness <= 5", name="check_review_cleanliness"
        ),
        CheckConstraint("accuracy >= 1 AND accuracy <= 5", name="check_review_accuracy"),
        CheckConstraint(
            "communication >= 1 AND communication <= 5",
            name="check_review_communication",
        ),
        CheckConstraint("location >= 1 AND location <= 5", name="check_review_location"),
        CheckConstraint(
            "check_in_rating >= 1 AND check_in_rating <= 5",
            name="check_review_check_in_rating",
        ),
        CheckConstraint("value >= 1 AND value <= 5", name="check_review_value"),
        CheckConstraint("rating >= 1.0 AND rating <= 5.0", name="check_review_rating_range"),
        CheckConstraint(
            "length(comment) >= 10 AND length(comment) <= 1000",
            name="check_review_comment_len",
        ),
        Index("idx_reviews_listing_created", "listing_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    booking_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False
    )
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    author_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    cleanliness: Mapped[int] = mapped_column(Integer, nullable=False)
    accuracy: Mapped[int] = mapped_column(Integer, nullable=False)
    communication: Mapped[int] = mapped_column(Integer, nullable=False)
    location: Mapped[int] = mapped_column(Integer, nullable=False)
    check_in_rating: Mapped[int] = mapped_column(Integer, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationships
    booking: Mapped["Booking"] = relationship("Booking", back_populates="review")
    listing: Mapped["Listing"] = relationship("Listing", back_populates="reviews")
    author: Mapped["User"] = relationship("User", back_populates="reviews")
