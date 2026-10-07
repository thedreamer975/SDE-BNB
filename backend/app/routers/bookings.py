"""
Bookings router: quote, create, list, get, cancel-preview, cancel, review.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.bookings import (
    BookingResponse,
    CancelPreviewResponse,
    CreateBookingRequest,
    CreateReviewRequest,
    QuoteParams,
    QuoteResponse,
)
from app.services.bookings import (
    cancel_booking,
    cancel_preview,
    create_booking,
    create_review,
    get_booking_by_id,
    get_guest_bookings,
)
from app.services.pricing import calculate_quote
from app.errors import NotFoundError
from app.models.listing import Listing
from app.core.dates import get_server_today as get_today

router = APIRouter(tags=["Bookings"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]


@router.get("/bookings/quote", response_model=QuoteResponse)
def quote_booking(
    listing_id: str,
    check_in: str,
    check_out: str,
    adults: int = Query(1, ge=1),
    children: int = Query(0, ge=0),
    infants: int = Query(0, ge=0),
    pets: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Calculate price breakdown for given listing + dates.
    Returns 404 if listing not found, 409 if dates unavailable.
    """
    listing = db.get(Listing, int(listing_id))
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    quote = calculate_quote(
        listing_id=int(listing_id),
        check_in=check_in,
        check_out=check_out,
        nightly_price_cents=listing.price_cents,
        cleaning_fee_cents=listing.cleaning_fee_cents,
    )
    return QuoteResponse(
        listing_id=listing_id,
        check_in=quote["check_in"],
        check_out=quote["check_out"],
        nights=quote["nights"],
        price_per_night=quote["nightly_cents"],
        nightly_total=quote["subtotal_cents"],
        cleaning_fee=quote["cleaning_cents"],
        service_fee=quote["service_cents"],
        total=quote["total_cents"],
    )


@router.post("/listings/{listing_id}/quote", response_model=QuoteResponse)
def quote_listing_post(
    listing_id: str,
    params: QuoteParams,
    db: Session = Depends(get_db),
):
    """Calculate price breakdown for given listing + dates (POST variant per PRD)."""
    listing = db.get(Listing, int(listing_id))
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    quote = calculate_quote(
        listing_id=int(listing_id),
        check_in=params.check_in,
        check_out=params.check_out,
        nightly_price_cents=listing.price_cents,
        cleaning_fee_cents=listing.cleaning_fee_cents,
    )
    return QuoteResponse(
        listing_id=listing_id,
        check_in=quote["check_in"],
        check_out=quote["check_out"],
        nights=quote["nights"],
        price_per_night=quote["nightly_cents"],
        nightly_total=quote["subtotal_cents"],
        cleaning_fee=quote["cleaning_cents"],
        service_fee=quote["service_cents"],
        total=quote["total_cents"],
    )


@router.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking_endpoint(
    body: CreateBookingRequest,
    db: DbDep,
    user: UserDep,
):
    """Create a confirmed booking (authoritative pricing, overlap-safe transaction)."""
    today_str = get_today()
    token = body.card_token or body.payment_token or "tok_visa_valid"
    result = create_booking(
        db=db,
        guest=user,
        listing_id=int(body.listing_id),
        check_in=body.check_in,
        check_out=body.check_out,
        adults=body.adults,
        children=body.children,
        infants=body.infants,
        pets=body.pets,
        card_token=token,
        today_str=today_str,
    )
    return BookingResponse(**result)


@router.get("/bookings", response_model=list[BookingResponse])
def list_bookings(
    db: DbDep,
    user: UserDep,
    tab: str = Query("all", pattern="^(all|upcoming|past)$"),
):
    """Get current user's bookings (guest view)."""
    today_str = get_today()
    results = get_guest_bookings(db, user.id, today_str, tab=tab)
    return [BookingResponse(**r) for r in results]


@router.get("/bookings/me")
def list_bookings_me(
    db: DbDep,
    user: UserDep,
    tab: str = Query("all", pattern="^(all|upcoming|past)$"),
):
    """Get current user's bookings per PRD spec."""
    today_str = get_today()
    results = get_guest_bookings(db, user.id, today_str, tab=tab)
    formatted = [BookingResponse(**r).model_dump() for r in results]
    return {"bookings": formatted}


@router.get("/bookings/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: str, db: DbDep, user: UserDep):
    """Get single booking (guest or host of that listing)."""
    today_str = get_today()
    result = get_booking_by_id(db, int(booking_id), user, today_str)
    return BookingResponse(**result)


@router.get("/bookings/{booking_id}/cancel-preview", response_model=CancelPreviewResponse)
def preview_cancel(booking_id: str, db: DbDep, user: UserDep):
    """Preview refund before cancelling."""
    today_str = get_today()
    result = cancel_preview(db, int(booking_id), user.id, today_str)
    return CancelPreviewResponse(**result)


@router.post("/bookings/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking_endpoint(booking_id: str, db: DbDep, user: UserDep):
    """Cancel a booking and process refund."""
    today_str = get_today()
    result = cancel_booking(db, int(booking_id), user.id, today_str)
    return BookingResponse(**result)


@router.post("/bookings/{booking_id}/review", status_code=201)
def create_review_endpoint(
    booking_id: str,
    body: CreateReviewRequest,
    db: DbDep,
    user: UserDep,
):
    """Submit a review for a completed stay."""
    today_str = get_today()
    result = create_review(
        db=db,
        booking_id=int(booking_id),
        guest_id=user.id,
        rating=body.rating,
        comment=body.comment,
        today_str=today_str,
    )
    return result
