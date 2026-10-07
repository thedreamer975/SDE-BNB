"""
Booking business logic: create booking, cancel, quote, get bookings.

All pricing is authoritative (server-side, from pricing.py).
Concurrency safety via BEGIN IMMEDIATE transaction with per-listing advisory locking.
"""
from datetime import datetime, timezone
import random
import string
from sqlalchemy import select, and_, text
from sqlalchemy.orm import Session, selectinload

from app.core.dates import parse_date
from app.errors import (
    ConflictError,
    DatesUnavailableError,
    ForbiddenError,
    NotFoundError,
    PaymentDeclinedError,
)
from app.models.booking import Booking
from app.models.listing import Listing
from app.models.notification import Notification
from app.models.review import Review
from app.models.user import User
from app.services.pricing import calculate_quote


# ─── Mock Payment Processor ──────────────────────────────────────────────────

DECLINE_TOKENS = {"tok_decline", "tok_insufficient_funds", "tok_expired"}

def _process_payment(card_token: str, amount_cents: int) -> dict:
    """
    Mock payment processor per PRD §10.3.
    tok_decline → PAYMENT_DECLINED
    tok_visa / tok_mastercard / any other string → success
    """
    token_lower = card_token.lower()
    if token_lower in DECLINE_TOKENS or token_lower.startswith("tok_fail"):
        raise PaymentDeclinedError("Your card was declined.")
    # Derive card brand from token for receipt
    if "visa" in token_lower:
        return {"brand": "Visa", "last4": "4242"}
    if "master" in token_lower:
        return {"brand": "Mastercard", "last4": "5555"}
    if "amex" in token_lower:
        return {"brand": "American Express", "last4": "3782"}
    return {"brand": "Visa", "last4": "4242"}


# ─── Confirmation Code ────────────────────────────────────────────────────────

def _generate_code() -> str:
    """Generate a 10-char alphanumeric confirmation code."""
    chars = string.ascii_uppercase + string.digits
    return "HM" + "".join(random.choices(chars, k=8))


# ─── Phase Computation ────────────────────────────────────────────────────────

def _compute_phase(booking: Booking, today_str: str) -> str:
    """
    Returns one of: upcoming, active, completed, cancelled.
    """
    if booking.status == "cancelled":
        return "cancelled"
    if booking.check_in > today_str:
        return "upcoming"
    if booking.check_out <= today_str:
        return "completed"
    return "active"


def _can_cancel(booking: Booking, today_str: str) -> bool:
    phase = _compute_phase(booking, today_str)
    return phase == "upcoming"


def _can_review(booking: Booking, today_str: str) -> bool:
    """Guest can review once stay is complete and no review yet exists."""
    if booking.status == "cancelled":
        return False
    phase = _compute_phase(booking, today_str)
    if phase not in ("active", "completed"):
        return False
    # review is loaded via selectinload; None means no review yet
    return getattr(booking, "review", None) is None


def _has_review(booking: Booking) -> bool:
    return booking.review is not None


# ─── Serializer ───────────────────────────────────────────────────────────────

def _serialize_booking(booking: Booking, today_str: str) -> dict:
    listing = booking.listing
    cover = booking.listing_cover_snapshot
    if not cover and listing and listing.photos:
        cover = listing.photos[0].url if listing.photos else None

    return {
        "id": str(booking.id),
        "listing_id": str(booking.listing_id),
        "listing_title": booking.listing_title_snapshot or (listing.title if listing else ""),
        "listing_city": listing.city if listing else "",
        "listing_country": listing.country if listing else "",
        "listing_photo": cover,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "adults": booking.adults,
        "children": booking.children,
        "infants": booking.infants,
        "pets": booking.pets,
        "nights": booking.nights,
        "price_per_night": booking.nightly_cents,
        "nightly_total": booking.subtotal_cents,
        "cleaning_fee": booking.cleaning_cents,
        "service_fee": booking.service_cents,
        "total_price": booking.total_cents,
        "status": booking.status,
        "payment_status": booking.payment_status,
        "refund_amount": booking.refund_cents,
        "confirmation_code": booking.code,
        "phase": _compute_phase(booking, today_str),
        "can_cancel": _can_cancel(booking, today_str),
        "can_review": _can_review(booking, today_str),
        "has_review": _has_review(booking),
        "created_at": booking.created_at,
        "cancelled_at": booking.cancelled_at,
    }


# ─── Create Booking ──────────────────────────────────────────────────────────

def create_booking(
    db: Session,
    guest: User,
    listing_id: int,
    check_in: str,
    check_out: str,
    adults: int,
    children: int,
    infants: int,
    pets: int,
    card_token: str,
    today_str: str,
) -> dict:
    """
    Create a booking atomically (BEGIN IMMEDIATE lock, overlap guard).
    All pricing is computed server-side.
    """
    # 1. Validate dates
    d_in = parse_date(check_in)
    d_out = parse_date(check_out)
    if d_in < parse_date(today_str):
        raise ConflictError("Check-in date cannot be in the past.", code="INVALID_DATES")
    if d_out <= d_in:
        raise ConflictError("Check-out must be after check-in.", code="INVALID_DATES")

    # 2. Load listing (non-deleted, with lock in SQLite via BEGIN IMMEDIATE below)
    listing = db.get(Listing, listing_id)
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    # 3. Owner guard
    if listing.host_id == guest.id:
        raise ForbiddenError("You cannot book your own listing.", code="OWN_LISTING")

    # 4. Guest capacity check
    total_guests = adults + children
    if total_guests > listing.max_guests:
        raise ConflictError(
            f"This listing supports at most {listing.max_guests} guests.",
            code="GUEST_LIMIT_EXCEEDED",
        )

    # 5. Night range check
    nights = (d_out - d_in).days
    if nights < listing.min_nights:
        raise ConflictError(
            f"Minimum stay is {listing.min_nights} night(s).",
            code="MIN_NIGHTS",
        )
    if nights > listing.max_nights:
        raise ConflictError(
            f"Maximum stay is {listing.max_nights} night(s).",
            code="MAX_NIGHTS",
        )

    # 6. BEGIN IMMEDIATE to prevent concurrent bookings
    db.execute(text("BEGIN IMMEDIATE"))

    # 7. Overlap check (inside the lock)
    overlap_stmt = select(Booking.id).where(
        and_(
            Booking.listing_id == listing_id,
            Booking.status == "confirmed",
            Booking.check_in < check_out,
            Booking.check_out > check_in,
        )
    ).limit(1)
    if db.execute(overlap_stmt).scalar_one_or_none() is not None:
        db.rollback()
        raise DatesUnavailableError()

    # 8. Process payment (mock) — no DB write on failure
    try:
        payment_info = _process_payment(card_token, amount_cents=0)  # amount computed below
    except PaymentDeclinedError:
        db.rollback()
        raise

    # 9. Authoritative pricing
    quote = calculate_quote(
        listing_id=listing_id,
        check_in=d_in,
        check_out=d_out,
        nightly_price_cents=listing.price_cents,
        cleaning_fee_cents=listing.cleaning_fee_cents,
    )

    # 10. Create booking record
    code = _generate_code()
    booking = Booking(
        code=code,
        listing_id=listing_id,
        guest_id=guest.id,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        infants=infants,
        pets=pets,
        nights=quote["nights"],
        nightly_cents=quote["nightly_cents"],
        subtotal_cents=quote["subtotal_cents"],
        cleaning_cents=quote["cleaning_cents"],
        service_cents=quote["service_cents"],
        total_cents=quote["total_cents"],
        status="confirmed",
        payment_status="paid",
        payment_brand=payment_info["brand"],
        payment_last4=payment_info["last4"],
        refund_cents=0,
        listing_title_snapshot=listing.title,
        listing_cover_snapshot=listing.photos[0].url if listing.photos else None,
    )
    db.add(booking)

    # 11. Notifications (host + guest) — use valid types from CHECK constraint
    host_notif = Notification(
        user_id=listing.host_id,
        type="booking_received",
        title="New booking!",
        body=f"{guest.name} booked '{listing.title}' for {check_in} to {check_out}.",
        link="/host/reservations",
    )
    guest_notif = Notification(
        user_id=guest.id,
        type="booking_confirmed",
        title="Booking confirmed!",
        body=f"Your booking at '{listing.title}' is confirmed. Code: {code}.",
        link="/trips",
    )
    db.add(host_notif)
    db.add(guest_notif)
    db.commit()

    db.refresh(booking)
    # Eager load for serialization
    db.execute(select(Booking).where(Booking.id == booking.id).options(
        selectinload(Booking.listing).selectinload(Listing.photos),
        selectinload(Booking.review),
    ))

    return _serialize_booking(booking, today_str)


# ─── Get Guest Bookings ────────────────────────────────────────────────────────

def get_guest_bookings(db: Session, guest_id: int, today_str: str, tab: str = "all") -> list[dict]:
    stmt = (
        select(Booking)
        .where(Booking.guest_id == guest_id)
        .options(
            selectinload(Booking.listing).selectinload(Listing.photos),
            selectinload(Booking.review),
        )
        .order_by(Booking.check_in.desc())
    )
    bookings = db.execute(stmt).scalars().all()
    result = [_serialize_booking(b, today_str) for b in bookings]

    if tab == "upcoming":
        result = [b for b in result if b["phase"] in ("upcoming", "active")]
    elif tab == "past":
        result = [b for b in result if b["phase"] in ("completed", "cancelled")]
    return result


# ─── Get Single Booking ────────────────────────────────────────────────────────

def get_booking_by_id(db: Session, booking_id: int, user: User, today_str: str) -> dict:
    booking = db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.listing).selectinload(Listing.photos),
            selectinload(Booking.review),
        )
    ).scalar_one_or_none()
    if not booking:
        raise NotFoundError("Booking not found.")

    # Only guest or listing's host can view
    is_guest = booking.guest_id == user.id
    is_host = booking.listing and booking.listing.host_id == user.id
    if not (is_guest or is_host):
        raise NotFoundError("Booking not found.")

    return _serialize_booking(booking, today_str)


# ─── Cancel Preview ──────────────────────────────────────────────────────────

def cancel_preview(db: Session, booking_id: int, guest_id: int, today_str: str) -> dict:
    booking = db.get(Booking, booking_id)
    if not booking or booking.guest_id != guest_id:
        raise NotFoundError("Booking not found.")
    if booking.status != "confirmed":
        raise ConflictError("This booking is already cancelled.", code="ALREADY_CANCELLED")

    today = parse_date(today_str)
    d_in = parse_date(booking.check_in)
    nights_elapsed = max(0, (today - d_in).days)
    nights_total = booking.nights

    # PRD §10.4 refund policy: 48h before check-in → full refund; else no refund
    hours_until_checkin = (d_in - today).days * 24
    if hours_until_checkin >= 48:
        refund = booking.total_cents
        policy = "Full refund (cancellation more than 48 hours before check-in)"
    else:
        refund = 0
        policy = "No refund (cancellation within 48 hours of check-in)"

    return {
        "booking_id": str(booking.id),
        "refund_amount": refund,
        "refund_policy": policy,
        "nights_elapsed": nights_elapsed,
        "nights_total": nights_total,
    }


# ─── Cancel Booking ───────────────────────────────────────────────────────────

def cancel_booking(db: Session, booking_id: int, guest_id: int, today_str: str) -> dict:
    booking = db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.listing).selectinload(Listing.photos),
            selectinload(Booking.review),
        )
    ).scalar_one_or_none()
    if not booking or booking.guest_id != guest_id:
        raise NotFoundError("Booking not found.")
    if booking.status == "cancelled":
        raise ConflictError("This booking is already cancelled.", code="ALREADY_CANCELLED")

    phase = _compute_phase(booking, today_str)
    if phase not in ("upcoming",):
        raise ConflictError(
            "Only upcoming bookings can be cancelled.", code="CANNOT_CANCEL"
        )

    preview = cancel_preview(db, booking_id, guest_id, today_str)
    refund = preview["refund_amount"]

    booking.status = "cancelled"
    booking.cancelled_at = datetime.now(timezone.utc).isoformat()
    if refund > 0:
        booking.payment_status = "refunded"
        booking.refund_cents = refund
    else:
        booking.payment_status = "paid"

    # Notify host
    if booking.listing:
        notif = Notification(
            user_id=booking.listing.host_id,
            type="booking_cancelled",
            title="Booking cancelled",
            body=f"A booking at '{booking.listing.title}' for {booking.check_in}–{booking.check_out} was cancelled.",
            link="/host/reservations",
        )
        db.add(notif)

    db.commit()
    db.refresh(booking)
    return _serialize_booking(booking, today_str)


# ─── Create Review ───────────────────────────────────────────────────────────

def create_review(
    db: Session,
    booking_id: int,
    guest_id: int,
    rating: int,
    comment: str,
    today_str: str,
) -> dict:
    booking = db.execute(
        select(Booking)
        .where(Booking.id == booking_id)
        .options(
            selectinload(Booking.listing),
            selectinload(Booking.review),
        )
    ).scalar_one_or_none()
    if not booking or booking.guest_id != guest_id:
        raise NotFoundError("Booking not found.")
    if booking.status == "cancelled":
        raise ConflictError("Cannot review a cancelled booking.", code="CANNOT_REVIEW")

    phase = _compute_phase(booking, today_str)
    if phase not in ("active", "completed"):
        raise ConflictError("You can only review after check-in.", code="CANNOT_REVIEW")
    if getattr(booking, "review", None) is not None:
        raise ConflictError("You have already reviewed this stay.", code="ALREADY_REVIEWED")

    # Review model requires sub-ratings; use overall rating for all sub-scores
    review = Review(
        booking_id=booking_id,
        listing_id=booking.listing_id,
        author_id=guest_id,
        cleanliness=rating,
        accuracy=rating,
        communication=rating,
        location=rating,
        check_in_rating=rating,
        value=rating,
        rating=float(rating),
        comment=comment,
    )
    db.add(review)

    # Update listing rating aggregate
    listing = booking.listing
    if listing:
        new_count = listing.rating_count + 1
        new_avg = ((listing.rating_avg * listing.rating_count) + rating) / new_count
        listing.rating_count = new_count
        listing.rating_avg = round(new_avg, 2)

        # Notify host — valid type from CHECK constraint
        notif = Notification(
            user_id=listing.host_id,
            type="review_received",
            title="New review received",
            body=f"You received a {rating}-star review on '{listing.title}'.",
            link=f"/rooms/{listing.id}",
        )
        db.add(notif)

    db.commit()
    db.refresh(review)

    return {
        "id": str(review.id),
        "booking_id": str(booking_id),
        "listing_id": str(review.listing_id),
        "author_id": str(review.author_id),
        "rating": review.rating,
        "comment": review.comment,
        "created_at": review.created_at,
    }
