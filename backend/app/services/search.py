import math
from typing import Any
from sqlalchemy import distinct, func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.errors import AppError
from app.models.amenity import listing_amenities
from app.models.booking import Booking
from app.models.listing import Listing
from app.models.user import User
from app.schemas.catalog import (
    HistogramBucket,
    ListingCardResponse,
    ListingCountResponse,
    ListingFacetsResponse,
    ListingListResponse,
    PhotoItem,
)
from app.services.wishlist import get_user_wishlist_ids


def build_search_query(filters: dict[str, Any], exclude_price: bool = False):
    """
    Construct the canonical SQL query for searching listings per PRD §10.5.
    Filters applied in SQL without business logic leaks.
    """
    query = select(Listing).where(Listing.deleted_at.is_(None))

    # 1. Location match (case-insensitive substring on city, country, or title)
    location = filters.get("location")
    if location and location.strip():
        loc_pattern = f"%{location.strip()}%"
        query = query.where(
            or_(
                Listing.city.ilike(loc_pattern),
                Listing.country.ilike(loc_pattern),
                Listing.title.ilike(loc_pattern),
            )
        )

    # 2. Guests & Pets
    adults = filters.get("adults", 0)
    children = filters.get("children", 0)
    total_guests = adults + children
    if total_guests > 0:
        query = query.where(Listing.max_guests >= total_guests)

    pets = filters.get("pets", 0)
    if pets > 0:
        query = query.where(Listing.pets_allowed == 1)

    # 3. Dates (both required per PRD §10.5; reject if only one provided)
    check_in = filters.get("check_in")
    check_out = filters.get("check_out")
    if (check_in and not check_out) or (check_out and not check_in):
        missing_field = "check_out" if check_in else "check_in"
        raise AppError(
            code="VALIDATION_ERROR",
            message="Both check_in and check_out dates must be provided.",
            status_code=422,
            fields={missing_field: "Both check_in and check_out are required."},
        )

    if check_in and check_out:
        if check_in >= check_out:
            raise AppError(
                code="VALIDATION_ERROR",
                message="check_out must be after check_in.",
                status_code=422,
                fields={"check_out": "Check-out date must be after check-in date."},
            )

        # Exclude listings having overlapping confirmed bookings (NOT EXISTS)
        overlap_subquery = (
            select(1)
            .where(
                Booking.listing_id == Listing.id,
                Booking.status == "confirmed",
                Booking.check_in < check_out,
                Booking.check_out > check_in,
            )
        )
        query = query.where(~overlap_subquery.exists())

    # 4. Category
    category = filters.get("category")
    if category and category.strip():
        query = query.where(Listing.category == category.strip())

    # 5. Room types (multi)
    room_types = filters.get("room_types")
    if room_types:
        query = query.where(Listing.room_type.in_(room_types))

    # 6. Property types (multi)
    property_types = filters.get("property_types")
    if property_types:
        query = query.where(Listing.property_type.in_(property_types))

    # 7. Price range (only if not excluding price for facets)
    if not exclude_price:
        min_price_cents = filters.get("min_price_cents")
        if min_price_cents is not None:
            query = query.where(Listing.price_cents >= min_price_cents)

        max_price_cents = filters.get("max_price_cents")
        if max_price_cents is not None:
            query = query.where(Listing.price_cents <= max_price_cents)

    # 8. Rooms, Beds, Baths
    min_bedrooms = filters.get("min_bedrooms")
    if min_bedrooms is not None:
        query = query.where(Listing.bedrooms >= min_bedrooms)

    min_beds = filters.get("min_beds")
    if min_beds is not None:
        query = query.where(Listing.beds >= min_beds)

    min_baths = filters.get("min_baths")
    if min_baths is not None:
        query = query.where(Listing.baths >= min_baths)

    # 9. Amenities (must contain ALL selected amenities)
    amenity_ids = filters.get("amenity_ids")
    if amenity_ids:
        amenity_subquery = (
            select(listing_amenities.c.listing_id)
            .where(listing_amenities.c.amenity_id.in_(amenity_ids))
            .group_by(listing_amenities.c.listing_id)
            .having(func.count(distinct(listing_amenities.c.amenity_id)) == len(amenity_ids))
        )
        query = query.where(Listing.id.in_(amenity_subquery))

    # 10. Superhost
    superhost = filters.get("superhost")
    if superhost:
        query = query.join(User, Listing.host_id == User.id).where(User.is_superhost == 1)

    return query


def listing_to_card(listing: Listing, saved: bool = False) -> ListingCardResponse:
    """Convert an ORM Listing to ListingCardResponse with derived badges and top 5 photos."""
    # Top 5 photos ordered by position
    photos_sorted = sorted(listing.photos, key=lambda p: p.position)[:5]
    photo_items = [
        PhotoItem(id=p.id, url=p.url, position=p.position, alt=p.alt)
        for p in photos_sorted
    ]

    is_superhost = bool(listing.host.is_superhost) if listing.host else False
    guest_favorite = bool(listing.rating_avg >= 4.8 and listing.rating_count >= 5)

    return ListingCardResponse(
        id=listing.id,
        title=listing.title,
        category=listing.category,
        property_type=listing.property_type,
        room_type=listing.room_type,
        city=listing.city,
        country=listing.country,
        latitude=listing.latitude,
        longitude=listing.longitude,
        price_cents=listing.price_cents,
        cleaning_fee_cents=listing.cleaning_fee_cents,
        max_guests=listing.max_guests,
        bedrooms=listing.bedrooms,
        beds=listing.beds,
        baths=listing.baths,
        pets_allowed=bool(listing.pets_allowed),
        rating_avg=listing.rating_avg,
        rating_count=listing.rating_count,
        is_superhost=is_superhost,
        guest_favorite=guest_favorite,
        photos=photo_items,
        saved=saved,
    )


def search_listings(
    db: Session,
    filters: dict[str, Any],
    page: int = 1,
    page_size: int = 20,
    user_id: int | None = None,
) -> ListingListResponse:
    """
    Search listings with pagination, eager loading, and saved-item hydration.
    """
    page = max(1, page)
    page_size = min(max(1, page_size), 40)
    offset = (page - 1) * page_size

    base_query = build_search_query(filters)

    # 1. Total count
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(count_query) or 0

    # 2. Paginated items with eager loading
    stmt = (
        base_query.options(
            selectinload(Listing.photos),
            selectinload(Listing.host),
        )
        .order_by(Listing.id.desc())
        .offset(offset)
        .limit(page_size)
    )
    listings = db.scalars(stmt).all()

    # 3. Hydrate saved flag if user authenticated
    saved_ids = set(get_user_wishlist_ids(db, user_id)) if user_id else set()

    items = [listing_to_card(listing, saved=(listing.id in saved_ids)) for listing in listings]
    has_more = (offset + len(items)) < total

    return ListingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        has_more=has_more,
    )


def count_listings(db: Session, filters: dict[str, Any]) -> ListingCountResponse:
    """Return total count of listings matching filters."""
    base_query = build_search_query(filters)
    count_query = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(count_query) or 0
    return ListingCountResponse(total=total)


def get_listing_facets(db: Session, filters: dict[str, Any]) -> ListingFacetsResponse:
    """
    Compute price facets (min, max, and 20-bucket histogram) across current
    filters excluding price limits (PRD §10.5).
    """
    base_query = build_search_query(filters, exclude_price=True)
    subq = base_query.subquery()

    # Get min and max price
    stats_query = select(
        func.min(subq.c.price_cents),
        func.max(subq.c.price_cents),
        func.count(subq.c.id),
    )
    min_p, max_p, count = db.execute(stats_query).one()

    if not count or min_p is None or max_p is None:
        return ListingFacetsResponse(price_min=0, price_max=0, histogram=[])

    if min_p == max_p:
        return ListingFacetsResponse(
            price_min=min_p,
            price_max=max_p,
            histogram=[HistogramBucket(from_cents=min_p, to_cents=max_p, count=count)],
        )

    # 20 buckets
    num_buckets = 20
    bucket_size = math.ceil((max_p - min_p) / num_buckets)

    # Fetch all prices for histogram calculation
    prices = list(db.scalars(select(subq.c.price_cents)).all())

    buckets = []
    for i in range(num_buckets):
        b_start = min_p + i * bucket_size
        b_end = b_start + bucket_size
        if i == num_buckets - 1:
            # Last bucket includes max_p
            b_count = sum(1 for p in prices if b_start <= p <= max_p)
        else:
            b_count = sum(1 for p in prices if b_start <= p < b_end)
        buckets.append(HistogramBucket(from_cents=b_start, to_cents=b_end, count=b_count))

    return ListingFacetsResponse(price_min=min_p, price_max=max_p, histogram=buckets)
