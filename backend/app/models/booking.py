from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
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
    from app.models.review import Review


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint("check_out > check_in", name="check_booking_dates_order"),
        CheckConstraint("adults >= 1", name="check_booking_adults_min"),
        CheckConstraint(
            "total_cents = subtotal_cents + cleaning_cents + service_cents",
            name="check_booking_total_math",
        ),
        CheckConstraint(
            "status IN ('confirmed', 'cancelled')",
            name="check_booking_status",
        ),
        CheckConstraint(
            "payment_status IN ('paid', 'refunded', 'partially_refunded')",
            name="check_booking_payment_status",
        ),
        Index(
            "idx_bookings_overlap",
            "listing_id",
            "status",
            "check_in",
            "check_out",
        ),
        Index(
            "idx_bookings_guest_status",
            "guest_id",
            "status",
            "check_in",
        ),
        Index("idx_bookings_code_unique", "code", unique=True),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    listing_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("listings.id", ondelete="CASCADE"), nullable=False
    )
    guest_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    check_in: Mapped[str] = mapped_column(String(10), nullable=False)
    check_out: Mapped[str] = mapped_column(String(10), nullable=False)
    adults: Mapped[int] = mapped_column(Integer, nullable=False)
    children: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    infants: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    pets: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    nights: Mapped[int] = mapped_column(Integer, nullable=False)
    nightly_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    subtotal_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    cleaning_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    service_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    total_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="confirmed")
    payment_status: Mapped[str] = mapped_column(String(30), nullable=False, default="paid")
    payment_brand: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    payment_last4: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    refund_cents: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cancelled_at: Mapped[Optional[str]] = mapped_column(String(35), nullable=True)
    listing_title_snapshot: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    listing_cover_snapshot: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationships
    listing: Mapped["Listing"] = relationship("Listing", back_populates="bookings")
    guest: Mapped["User"] = relationship("User", back_populates="bookings")
    review: Mapped[Optional["Review"]] = relationship(
        "Review", back_populates="booking", uselist=False
    )
