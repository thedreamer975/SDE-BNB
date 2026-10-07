from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload
from app.db import get_db
from app.deps import get_current_user_optional
from app.errors import NotFoundError
from app.models.listing import Listing
from app.models.review import Review
from app.models.user import User
from app.schemas.catalog import (
    AvailabilityResponse,
    DestinationSuggestion,
    HostSummary,
    ListingCountResponse,
    ListingDetailResponse,
    ListingFacetsResponse,
    ListingListResponse,
    PhotoItem,
    ReviewAuthor,
    ReviewItem,
    ReviewsListResponse,
    ReviewsSummary,
)
from app.schemas.meta import AmenityItem
from app.services.availability import get_booked_ranges
from app.services.search import (
    count_listings,
    get_listing_facets,
    search_listings,
)
from app.services.wishlist import get_user_wishlist_ids
from seed.data import DESTINATIONS_DATA

router = APIRouter(tags=["Catalog"])


@router.get("/search/suggestions", response_model=list[DestinationSuggestion])
def get_search_suggestions(q: str = "") -> list[DestinationSuggestion]:
    """
    Return destination suggestions matching q (prefix/substring on city or country),
    plus static Anywhere and Nearby options per PRD §8.3.
    """
    cleaned_q = q.strip().lower()

    static_options = [
        DestinationSuggestion(label="I'm flexible (Anywhere)", city=None, country=None, lat=None, lng=None),
        DestinationSuggestion(label="Nearby stays", city=None, country=None, lat=None, lng=None),
    ]

    matched_destinations: list[DestinationSuggestion] = []
    for d in DESTINATIONS_DATA:
        city_lower = d["city"].lower()
        country_lower = d["country"].lower()
        if not cleaned_q or cleaned_q in city_lower or cleaned_q in country_lower:
            matched_destinations.append(
                DestinationSuggestion(
                    label=f"{d['city']}, {d['country']}",
                    city=d["city"],
                    country=d["country"],
                    lat=d["lat"],
                    lng=d["lng"],
                )
            )

    # Top 6 matching
    top_matches = matched_destinations[:6]

    if not cleaned_q:
        return static_options + top_matches

    return top_matches if top_matches else static_options


def extract_filter_params(
    location: str | None = None,
    check_in: str | None = None,
    check_out: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    pets: int = 0,
    category: str | None = None,
    room_types: list[str] | None = None,
    property_types: list[str] | None = None,
    min_price_cents: int | None = None,
    max_price_cents: int | None = None,
    min_bedrooms: int | None = None,
    min_beds: int | None = None,
    min_baths: float | None = None,
    amenity_ids: list[int] | None = None,
    superhost: bool = False,
) -> dict:
    return {
        "location": location,
        "check_in": check_in,
        "check_out": check_out,
        "adults": adults,
        "children": children,
        "infants": infants,
        "pets": pets,
        "category": category,
        "room_types": room_types,
        "property_types": property_types,
        "min_price_cents": min_price_cents,
        "max_price_cents": max_price_cents,
        "min_bedrooms": min_bedrooms,
        "min_beds": min_beds,
        "min_baths": min_baths,
        "amenity_ids": amenity_ids,
        "superhost": superhost,
    }


@router.get("/listings", response_model=ListingListResponse)
def get_listings(
    location: str | None = None,
    check_in: str | None = None,
    check_out: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    pets: int = 0,
    category: str | None = None,
    room_types: Annotated[list[str] | None, Query()] = None,
    property_types: Annotated[list[str] | None, Query()] = None,
    min_price_cents: int | None = None,
    max_price_cents: int | None = None,
    min_bedrooms: int | None = None,
    min_beds: int | None = None,
    min_baths: float | None = None,
    amenity_ids: Annotated[list[int] | None, Query()] = None,
    superhost: bool = False,
    page: int = 1,
    page_size: int = 20,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Search and filter catalog listings with pagination and saved state."""
    filters = extract_filter_params(
        location=location,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        infants=infants,
        pets=pets,
        category=category,
        room_types=room_types,
        property_types=property_types,
        min_price_cents=min_price_cents,
        max_price_cents=max_price_cents,
        min_bedrooms=min_bedrooms,
        min_beds=min_beds,
        min_baths=min_baths,
        amenity_ids=amenity_ids,
        superhost=superhost,
    )
    user_id = user.id if user else None
    return search_listings(db, filters, page=page, page_size=page_size, user_id=user_id)


@router.get("/listings/count", response_model=ListingCountResponse)
def get_listings_count(
    location: str | None = None,
    check_in: str | None = None,
    check_out: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    pets: int = 0,
    category: str | None = None,
    room_types: Annotated[list[str] | None, Query()] = None,
    property_types: Annotated[list[str] | None, Query()] = None,
    min_price_cents: int | None = None,
    max_price_cents: int | None = None,
    min_bedrooms: int | None = None,
    min_beds: int | None = None,
    min_baths: float | None = None,
    amenity_ids: Annotated[list[int] | None, Query()] = None,
    superhost: bool = False,
    db: Session = Depends(get_db),
):
    """Return total count of listings matching filters for filter dialog live preview."""
    filters = extract_filter_params(
        location=location,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        infants=infants,
        pets=pets,
        category=category,
        room_types=room_types,
        property_types=property_types,
        min_price_cents=min_price_cents,
        max_price_cents=max_price_cents,
        min_bedrooms=min_bedrooms,
        min_beds=min_beds,
        min_baths=min_baths,
        amenity_ids=amenity_ids,
        superhost=superhost,
    )
    return count_listings(db, filters)


@router.get("/listings/facets", response_model=ListingFacetsResponse)
def get_facets(
    location: str | None = None,
    check_in: str | None = None,
    check_out: str | None = None,
    adults: int = 1,
    children: int = 0,
    infants: int = 0,
    pets: int = 0,
    category: str | None = None,
    room_types: Annotated[list[str] | None, Query()] = None,
    property_types: Annotated[list[str] | None, Query()] = None,
    min_bedrooms: int | None = None,
    min_beds: int | None = None,
    min_baths: float | None = None,
    amenity_ids: Annotated[list[int] | None, Query()] = None,
    superhost: bool = False,
    db: Session = Depends(get_db),
):
    """Return price facets and 20-bucket histogram for current filters."""
    filters = extract_filter_params(
        location=location,
        check_in=check_in,
        check_out=check_out,
        adults=adults,
        children=children,
        infants=infants,
        pets=pets,
        category=category,
        room_types=room_types,
        property_types=property_types,
        min_bedrooms=min_bedrooms,
        min_beds=min_beds,
        min_baths=min_baths,
        amenity_ids=amenity_ids,
        superhost=superhost,
    )
    return get_listing_facets(db, filters)


@router.get("/listings/{listing_id}", response_model=ListingDetailResponse)
def get_listing_detail(
    listing_id: int,
    user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """Return full listing details, photos, amenities, host summary, and saved state."""
    stmt = (
        select(Listing)
        .where(Listing.id == listing_id, Listing.deleted_at.is_(None))
        .options(
            selectinload(Listing.photos),
            selectinload(Listing.amenities),
            selectinload(Listing.host),
        )
    )
    listing = db.scalar(stmt)
    if not listing:
        raise NotFoundError("Listing not found.")

    saved = False
    if user:
        saved = listing_id in set(get_user_wishlist_ids(db, user.id))

    # Calculate host listing count
    host_listings_count = db.scalar(
        select(func.count(Listing.id)).where(
            Listing.host_id == listing.host_id,
            Listing.deleted_at.is_(None),
        )
    ) or 1

    joined_year = datetime.now().year
    if hasattr(listing.host.created_at, "year"):
        joined_year = listing.host.created_at.year
    elif isinstance(listing.host.created_at, str) and len(listing.host.created_at) >= 4:
        try:
            joined_year = int(listing.host.created_at[:4])
        except ValueError:
            pass

    host_summary = HostSummary(
        id=listing.host.id,
        name=listing.host.name,
        avatar_url=listing.host.avatar_url,
        is_superhost=bool(listing.host.is_superhost),
        joined_year=joined_year,
        listing_count=host_listings_count,
    )

    photos_sorted = sorted(listing.photos, key=lambda p: p.position)
    photo_items = [
        PhotoItem(id=p.id, url=p.url, position=p.position, alt=p.alt)
        for p in photos_sorted
    ]

    amenity_items = [
        AmenityItem(id=a.id, name=a.name, icon_key=a.icon_key, group=a.group)
        for a in listing.amenities
    ]

    guest_favorite = bool(listing.rating_avg >= 4.8 and listing.rating_count >= 5)

    return ListingDetailResponse(
        id=listing.id,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        property_type=listing.property_type,
        room_type=listing.room_type,
        address_line=listing.address_line,
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
        check_in_time=listing.check_in_time,
        check_out_time=listing.check_out_time,
        min_nights=listing.min_nights,
        max_nights=listing.max_nights,
        house_rules=listing.house_rules,
        rating_avg=listing.rating_avg,
        rating_count=listing.rating_count,
        guest_favorite=guest_favorite,
        host=host_summary,
        photos=photo_items,
        amenities=amenity_items,
        saved=saved,
    )


@router.get("/listings/{listing_id}/availability", response_model=AvailabilityResponse)
def get_availability(
    listing_id: int,
    from_date: str | None = Query(None, alias="from"),
    to_date: str | None = Query(None, alias="to"),
    db: Session = Depends(get_db),
):
    """Return booked date ranges and constraints for availability calendar."""
    data = get_booked_ranges(db, listing_id, from_date, to_date)
    return AvailabilityResponse(**data)


@router.get("/listings/{listing_id}/reviews", response_model=ReviewsListResponse)
def get_listing_reviews(
    listing_id: int,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db),
):
    """Return paginated reviews and aggregate categories breakdown for a listing."""
    listing = db.get(Listing, listing_id)
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    page = max(1, page)
    page_size = min(max(1, page_size), 50)
    offset = (page - 1) * page_size

    # Count reviews
    count_query = select(func.count(Review.id)).where(Review.listing_id == listing_id)
    total = db.scalar(count_query) or 0

    # Subscore category averages
    cat_query = select(
        func.avg(Review.cleanliness),
        func.avg(Review.accuracy),
        func.avg(Review.communication),
        func.avg(Review.location),
        func.avg(Review.check_in_rating),
        func.avg(Review.value),
    ).where(Review.listing_id == listing_id)
    cat_res = db.execute(cat_query).one()

    def clean_avg(val):
        return round(float(val), 2) if val is not None else 0.0

    categories_summary = {
        "cleanliness": clean_avg(cat_res[0]),
        "accuracy": clean_avg(cat_res[1]),
        "communication": clean_avg(cat_res[2]),
        "location": clean_avg(cat_res[3]),
        "check_in": clean_avg(cat_res[4]),
        "value": clean_avg(cat_res[5]),
    }

    # Paginated review rows with author
    stmt = (
        select(Review)
        .where(Review.listing_id == listing_id)
        .options(selectinload(Review.author))
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(page_size)
    )
    reviews = db.scalars(stmt).all()

    items = [
        ReviewItem(
            id=r.id,
            author=ReviewAuthor(
                id=r.author.id,
                name=r.author.name,
                avatar_url=r.author.avatar_url,
            ),
            cleanliness=r.cleanliness,
            accuracy=r.accuracy,
            communication=r.communication,
            location=r.location,
            check_in_rating=r.check_in_rating,
            value=r.value,
            rating=r.rating,
            comment=r.comment,
            created_at=r.created_at,
        )
        for r in reviews
    ]

    has_more = (offset + len(items)) < total

    return ReviewsListResponse(
        items=items,
        summary=ReviewsSummary(
            avg=listing.rating_avg,
            count=listing.rating_count,
            categories=categories_summary,
        ),
        total=total,
        has_more=has_more,
    )
