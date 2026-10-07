"""
Host-side business logic: listing CRUD, dashboard summary, reservations.
"""
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func, and_
from sqlalchemy.orm import Session, selectinload

from app.core.dates import parse_date
from app.errors import ConflictError, ForbiddenError, NotFoundError
from app.models.amenity import Amenity
from app.models.booking import Booking
from app.models.listing import Listing, ListingPhoto
from app.models.user import User


# ─── Serializers ──────────────────────────────────────────────────────────────

def _upcoming_booking_count(db: Session, listing_id: int, today_str: str) -> int:
    """Count confirmed bookings with check_in >= today."""
    result = db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.listing_id == listing_id,
                Booking.status == "confirmed",
                Booking.check_in >= today_str,
            )
        )
    ).scalar_one()
    return result or 0


def _serialize_host_listing(listing: Listing, today_str: str) -> dict:
    upcoming = _upcoming_booking_count.__wrapped__(listing.id) if hasattr(_upcoming_booking_count, "__wrapped__") else 0
    photos = [p.url for p in listing.photos]
    return {
        "id": str(listing.id),
        "title": listing.title,
        "city": listing.city,
        "country": listing.country,
        "price_per_night": listing.price_cents,
        "rating_avg": listing.rating_avg,
        "rating_count": listing.rating_count,
        "photos": photos,
        "upcoming_bookings": upcoming,
        "is_active": listing.deleted_at is None,
    }


def _serialize_host_listing_full(listing: Listing, db: Session, today_str: str) -> dict:
    upcoming = _upcoming_booking_count(db, listing.id, today_str)
    photos = [p.url for p in listing.photos]
    return {
        "id": str(listing.id),
        "title": listing.title,
        "city": listing.city,
        "country": listing.country,
        "price_per_night": listing.price_cents,
        "rating_avg": listing.rating_avg,
        "rating_count": listing.rating_count,
        "photos": photos,
        "upcoming_bookings": upcoming,
        "is_active": listing.deleted_at is None,
    }


# ─── Get Host Listings ────────────────────────────────────────────────────────

def get_host_listings(db: Session, host_id: int, today_str: str) -> list[dict]:
    listings = db.execute(
        select(Listing)
        .where(and_(Listing.host_id == host_id, Listing.deleted_at.is_(None)))
        .options(selectinload(Listing.photos))
        .order_by(Listing.created_at.desc())
    ).scalars().all()
    return [_serialize_host_listing_full(listing, db, today_str) for listing in listings]


# ─── Create Listing ───────────────────────────────────────────────────────────

def create_listing(db: Session, host: User, data: dict) -> Listing:
    """
    Create a listing from validated data dict.
    Atomically replaces photos and amenities.
    """
    # Validate amenity ids exist
    amenity_ids = data.get("amenity_ids", [])
    amenities = []
    if amenity_ids:
        amenities = db.execute(
            select(Amenity).where(Amenity.id.in_(amenity_ids))
        ).scalars().all()
        if len(amenities) != len(set(amenity_ids)):
            raise ConflictError("One or more amenity IDs are invalid.", code="INVALID_AMENITY")

    listing = Listing(
        host_id=host.id,
        title=data["title"],
        description=data["description"],
        category=data["category"],
        property_type=data["property_type"],
        room_type=data["room_type"],
        address_line=data.get("address"),
        city=data["city"],
        country=data["country"],
        latitude=data["latitude"],
        longitude=data["longitude"],
        max_guests=data["max_guests"],
        bedrooms=data["bedrooms"],
        beds=data["beds"],
        baths=data["baths"],
        pets_allowed=1 if data.get("pets_allowed") else 0,
        price_cents=data["price_per_night"],
        cleaning_fee_cents=data.get("cleaning_fee", 0),
        min_nights=data.get("min_nights", 1),
        max_nights=data.get("max_nights", 30),
        check_in_time=data.get("check_in_time", "15:00"),
        check_out_time=data.get("check_out_time", "11:00"),
        house_rules=data.get("house_rules"),
    )
    db.add(listing)
    db.flush()  # get listing.id

    # Attach photos (positional)
    for photo_data in data.get("photos", []):
        photo = ListingPhoto(
            listing_id=listing.id,
            url=photo_data["url"],
            position=photo_data["position"],
            alt=photo_data.get("alt"),
        )
        db.add(photo)

    # Attach amenities via M2M
    listing.amenities = amenities

    db.commit()
    db.refresh(listing)
    return listing


# ─── Update Listing ───────────────────────────────────────────────────────────

def update_listing(db: Session, listing_id: int, host_id: int, data: dict) -> Listing:
    listing = db.execute(
        select(Listing)
        .where(and_(Listing.id == listing_id, Listing.deleted_at.is_(None)))
        .options(selectinload(Listing.photos), selectinload(Listing.amenities))
    ).scalar_one_or_none()
    if not listing:
        raise NotFoundError("Listing not found.")
    if listing.host_id != host_id:
        raise ForbiddenError("You don't own this listing.")

    scalar_fields = [
        ("title", "title"), ("description", "description"), ("category", "category"),
        ("property_type", "property_type"), ("room_type", "room_type"),
        ("address", "address_line"), ("city", "city"), ("country", "country"),
        ("latitude", "latitude"), ("longitude", "longitude"),
        ("max_guests", "max_guests"), ("bedrooms", "bedrooms"),
        ("beds", "beds"), ("baths", "baths"),
        ("price_per_night", "price_cents"), ("cleaning_fee", "cleaning_fee_cents"),
        ("min_nights", "min_nights"), ("max_nights", "max_nights"),
        ("check_in_time", "check_in_time"), ("check_out_time", "check_out_time"),
        ("house_rules", "house_rules"),
    ]
    for src_key, dst_attr in scalar_fields:
        if src_key in data and data[src_key] is not None:
            setattr(listing, dst_attr, data[src_key])

    if "pets_allowed" in data and data["pets_allowed"] is not None:
        listing.pets_allowed = 1 if data["pets_allowed"] else 0

    # Replace photos atomically if provided
    if "photos" in data and data["photos"] is not None:
        for old_photo in list(listing.photos):
            db.delete(old_photo)
        db.flush()
        for photo_data in data["photos"]:
            photo = ListingPhoto(
                listing_id=listing.id,
                url=photo_data["url"],
                position=photo_data["position"],
                alt=photo_data.get("alt"),
            )
            db.add(photo)

    # Replace amenities if provided
    if "amenity_ids" in data and data["amenity_ids"] is not None:
        amenities = db.execute(
            select(Amenity).where(Amenity.id.in_(data["amenity_ids"]))
        ).scalars().all()
        listing.amenities = amenities

    db.commit()
    db.refresh(listing)
    return listing


# ─── Delete Listing ───────────────────────────────────────────────────────────

def delete_listing(db: Session, listing_id: int, host_id: int, today_str: str) -> None:
    listing = db.get(Listing, listing_id)
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")
    if listing.host_id != host_id:
        raise ForbiddenError("You don't own this listing.")

    # Check for upcoming confirmed bookings
    upcoming = db.execute(
        select(func.count(Booking.id)).where(
            and_(
                Booking.listing_id == listing_id,
                Booking.status == "confirmed",
                Booking.check_out > today_str,
            )
        )
    ).scalar_one()
    if upcoming > 0:
        raise ConflictError(
            f"Cannot delete: listing has {upcoming} upcoming booking(s).",
            code="LISTING_HAS_UPCOMING_BOOKINGS",
        )

    listing.deleted_at = datetime.now(timezone.utc).isoformat()
    db.commit()


# ─── Get Single Host Listing ──────────────────────────────────────────────────

def get_host_listing(db: Session, listing_id: int, host_id: int, today_str: str) -> dict:
    listing = db.execute(
        select(Listing)
        .where(and_(Listing.id == listing_id, Listing.deleted_at.is_(None)))
        .options(selectinload(Listing.photos), selectinload(Listing.amenities))
    ).scalar_one_or_none()
    if not listing:
        raise NotFoundError("Listing not found.")
    if listing.host_id != host_id:
        raise ForbiddenError("You don't own this listing.")
    return _serialize_host_listing_full(listing, db, today_str)


# ─── Host Reservations ────────────────────────────────────────────────────────

def get_host_reservations(
    db: Session,
    host_id: int,
    today_str: str,
    tab: str = "all",
    listing_id: int | None = None,
) -> list[dict]:
    """
    Return all reservations for listings owned by host_id.
    Optionally filter by tab (upcoming/past) and listing_id.
    """
    stmt = (
        select(Booking)
        .join(Listing, Booking.listing_id == Listing.id)
        .where(and_(Listing.host_id == host_id))
        .options(
            selectinload(Booking.listing).selectinload(Listing.photos),
            selectinload(Booking.review),
        )
        .order_by(Booking.check_in.desc())
    )
    if listing_id is not None:
        stmt = stmt.where(Booking.listing_id == listing_id)

    if tab == "upcoming":
        stmt = stmt.where(and_(Booking.status == "confirmed", Booking.check_in >= today_str))
    elif tab == "past":
        stmt = stmt.where(Booking.check_out < today_str)

    bookings = db.execute(stmt).scalars().all()

    from app.services.bookings import _serialize_booking
    return [_serialize_booking(b, today_str) for b in bookings]


# ─── Host Dashboard ───────────────────────────────────────────────────────────

def get_host_dashboard(db: Session, host_id: int, today_str: str) -> dict:
    """
    Compute dashboard metrics for a host.
    """
    today = parse_date(today_str)
    thirty_days_ago = (today - timedelta(days=30)).strftime("%Y-%m-%d")

    # All host listing IDs (non-deleted)
    listing_ids_result = db.execute(
        select(Listing.id).where(and_(Listing.host_id == host_id, Listing.deleted_at.is_(None)))
    ).scalars().all()
    listing_ids = list(listing_ids_result)
    total_listings = len(listing_ids)

    if not listing_ids:
        return {
            "checking_out": 0,
            "currently_hosting": 0,
            "arriving_soon": 0,
            "upcoming": 0,
            "total_listings": 0,
            "upcoming_bookings": 0,
            "revenue_30d": 0,
            "avg_rating": 0.0,
        }

    base = and_(Booking.listing_id.in_(listing_ids), Booking.status == "confirmed")

    checking_out = db.execute(
        select(func.count(Booking.id)).where(and_(base, Booking.check_out == today_str))
    ).scalar_one() or 0

    currently_hosting = db.execute(
        select(func.count(Booking.id)).where(
            and_(base, Booking.check_in <= today_str, Booking.check_out > today_str)
        )
    ).scalar_one() or 0

    # Arriving in next 3 days
    three_days = (today + timedelta(days=3)).strftime("%Y-%m-%d")
    arriving_soon = db.execute(
        select(func.count(Booking.id)).where(
            and_(base, Booking.check_in > today_str, Booking.check_in <= three_days)
        )
    ).scalar_one() or 0

    upcoming = db.execute(
        select(func.count(Booking.id)).where(and_(base, Booking.check_in >= today_str))
    ).scalar_one() or 0

    # Revenue from bookings completed in last 30 days
    revenue_30d = db.execute(
        select(func.coalesce(func.sum(Booking.total_cents), 0)).where(
            and_(
                Booking.listing_id.in_(listing_ids),
                Booking.status == "confirmed",
                Booking.check_in >= thirty_days_ago,
                Booking.check_in <= today_str,
            )
        )
    ).scalar_one() or 0

    # Average rating across all host listings
    avg_rating_result = db.execute(
        select(func.avg(Listing.rating_avg)).where(
            and_(
                Listing.host_id == host_id,
                Listing.deleted_at.is_(None),
                Listing.rating_count > 0,
            )
        )
    ).scalar_one()
    avg_rating = round(float(avg_rating_result), 2) if avg_rating_result else 0.0

    return {
        "checking_out": checking_out,
        "currently_hosting": currently_hosting,
        "arriving_soon": arriving_soon,
        "upcoming": upcoming,
        "total_listings": total_listings,
        "upcoming_bookings": upcoming,
        "revenue_30d": revenue_30d,
        "avg_rating": avg_rating,
    }
