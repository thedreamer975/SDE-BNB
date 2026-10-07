from datetime import timedelta
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from app.core.dates import format_date, get_server_today, parse_date
from app.errors import NotFoundError
from app.models.booking import Booking
from app.models.listing import Listing


def check_date_overlap_query(listing_id: int, check_in: str, check_out: str):
    """
    Return SQLAlchemy expression for confirmed booking date overlap on [check_in, check_out).
    Overlap condition: existing.check_in < check_out AND existing.check_out > check_in.
    """
    return and_(
        Booking.listing_id == listing_id,
        Booking.status == "confirmed",
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    )


def has_booking_overlap(db: Session, listing_id: int, check_in: str, check_out: str) -> bool:
    """Return True if any confirmed booking on listing overlaps with [check_in, check_out)."""
    stmt = select(Booking.id).where(check_date_overlap_query(listing_id, check_in, check_out)).limit(1)
    return db.scalar(stmt) is not None


def get_booked_ranges(
    db: Session,
    listing_id: int,
    from_date: str | None = None,
    to_date: str | None = None,
) -> dict:
    """
    Return booked ranges and booking constraints for a listing per PRD §8.3:
    {booked: [{check_in, check_out}], min_nights, max_nights, max_advance_days: 365}
    Defaults range: today -> today + 365 days.
    """
    listing = db.get(Listing, listing_id)
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    today_str = get_server_today()
    if not from_date:
        from_date = today_str
    if not to_date:
        today_dt = parse_date(today_str)
        to_date = format_date(today_dt + timedelta(days=365))

    stmt = (
        select(Booking)
        .where(
            Booking.listing_id == listing_id,
            Booking.status == "confirmed",
            Booking.check_out > from_date,
            Booking.check_in < to_date,
        )
        .order_by(Booking.check_in.asc())
    )
    bookings = db.scalars(stmt).all()

    booked = [{"check_in": b.check_in, "check_out": b.check_out} for b in bookings]

    return {
        "booked": booked,
        "min_nights": listing.min_nights,
        "max_nights": listing.max_nights,
        "max_advance_days": 365,
    }
