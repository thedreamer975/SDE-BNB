from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.amenity import Amenity
from app.models.booking import Booking
from app.models.listing import Listing, ListingPhoto
from app.models.review import Review
from app.models.user import User


@pytest.fixture
def catalog_data(db_session: Session):
    """Seed structured, predictable test listings, photos, amenities, reviews, and bookings."""
    # Hosts
    host_super = User(
        name="Superhost Host",
        email="super@demo.com",
        password_hash="dummy",
        role="host",
        is_superhost=1,
    )
    host_regular = User(
        name="Regular Host",
        email="regular@demo.com",
        password_hash="dummy",
        role="host",
        is_superhost=0,
    )
    guest = User(
        name="Reviewer Guest",
        email="guest_rev@demo.com",
        password_hash="dummy",
        role="guest",
    )
    db_session.add_all([host_super, host_regular, guest])
    db_session.flush()

    # Amenities
    a_wifi = Amenity(name="Fast Wifi", icon_key="wifi", group="Essentials")
    a_pool = Amenity(name="Private pool", icon_key="waves", group="Features")
    a_ac = Amenity(name="Air conditioning", icon_key="wind", group="Essentials")
    db_session.add_all([a_wifi, a_pool, a_ac])
    db_session.flush()

    # Listing 1: Goa, Beachfront, Villa, $150, Superhost, Fast Wifi + Pool, 4 guests, 2 bed, 2 baths
    l1 = Listing(
        host_id=host_super.id,
        title="Sunset Beach Villa Goa",
        description="Luxury villa on the beach",
        category="Beachfront",
        property_type="Villa",
        room_type="entire_home",
        address_line="12 Beach Rd",
        city="Goa",
        country="India",
        latitude=15.29,
        longitude=74.12,
        price_cents=15000,
        cleaning_fee_cents=3000,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=2.0,
        pets_allowed=1,
        min_nights=2,
        max_nights=30,
        rating_avg=4.9,
        rating_count=6,
    )
    l1.amenities = [a_wifi, a_pool]
    l1.photos = [
        ListingPhoto(url="https://images.unsplash.com/p1", position=1, alt="Cover"),
        ListingPhoto(url="https://images.unsplash.com/p2", position=2, alt="Living"),
    ]

    # Listing 2: Goa, Trending, Apartment, $80, Regular host, Fast Wifi only, 2 guests, 1 bed, 1 bath
    l2 = Listing(
        host_id=host_regular.id,
        title="Cozy Old Town Apartment",
        description="Charming apartment in Goa",
        category="Trending",
        property_type="Apartment",
        room_type="entire_home",
        address_line="44 Old Town",
        city="Goa",
        country="India",
        latitude=15.30,
        longitude=74.13,
        price_cents=8000,
        cleaning_fee_cents=1500,
        max_guests=2,
        bedrooms=1,
        beds=1,
        baths=1.0,
        pets_allowed=0,
        min_nights=1,
        max_nights=14,
        rating_avg=4.5,
        rating_count=3,
    )
    l2.amenities = [a_wifi]
    l2.photos = [
        ListingPhoto(url="https://images.unsplash.com/p3", position=1, alt="Apartment"),
    ]

    # Listing 3: Manali, Cabins, Cabin, $220, Superhost, AC + Pool, 6 guests, 3 bed, 2.5 baths
    l3 = Listing(
        host_id=host_super.id,
        title="Alpine Pine Cabin Manali",
        description="Pine cabin with mountain views",
        category="Cabins",
        property_type="Cabin",
        room_type="entire_home",
        address_line="88 Mountain Rd",
        city="Manali",
        country="India",
        latitude=32.23,
        longitude=77.18,
        price_cents=22000,
        cleaning_fee_cents=4000,
        max_guests=6,
        bedrooms=3,
        beds=4,
        baths=2.5,
        pets_allowed=1,
        min_nights=3,
        max_nights=30,
        rating_avg=4.95,
        rating_count=8,
    )
    l3.amenities = [a_ac, a_pool]
    l3.photos = [
        ListingPhoto(url="https://images.unsplash.com/p4", position=1, alt="Cabin"),
    ]

    db_session.add_all([l1, l2, l3])
    db_session.flush()

    # Confirmed booking on Listing 1: 2026-11-05 to 2026-11-10
    booking1 = Booking(
        code="BKGOA11105",
        listing_id=l1.id,
        guest_id=guest.id,
        check_in="2026-11-05",
        check_out="2026-11-10",
        adults=2,
        nights=5,
        nightly_cents=15000,
        subtotal_cents=75000,
        cleaning_cents=3000,
        service_cents=9000,
        total_cents=87000,
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(booking1)
    db_session.flush()

    # Review on Listing 1
    rev1 = Review(
        booking_id=booking1.id,
        listing_id=l1.id,
        author_id=guest.id,
        cleanliness=5,
        accuracy=5,
        communication=5,
        location=5,
        check_in_rating=5,
        value=5,
        rating=5.0,
        comment="Incredible villa, crystal clear pool!",
    )
    db_session.add(rev1)
    db_session.commit()

    return {
        "l1": l1,
        "l2": l2,
        "l3": l3,
        "a_wifi": a_wifi,
        "a_pool": a_pool,
        "a_ac": a_ac,
        "host_super": host_super,
        "host_regular": host_regular,
    }


def test_meta_endpoint(client: TestClient, catalog_data):
    res = client.get("/api/meta")
    assert res.status_code == 200
    data = res.json()
    assert "today" in data
    assert len(data["categories"]) > 5
    assert len(data["property_types"]) > 3
    assert len(data["amenities"]) >= 3
    assert data["limits"]["max_guests"] == 16


def test_search_suggestions(client: TestClient):
    # Empty query returns static options + destinations
    res = client.get("/api/search/suggestions")
    assert res.status_code == 200
    suggestions = res.json()
    assert any(s["label"] == "I'm flexible (Anywhere)" for s in suggestions)
    assert any(s["label"] == "Nearby stays" for s in suggestions)

    # Filtered query
    res_goa = client.get("/api/search/suggestions?q=goa")
    assert res_goa.status_code == 200
    labels = [s["label"] for s in res_goa.json()]
    assert any("Goa" in label for label in labels)


def test_search_filter_by_location(client: TestClient, catalog_data):
    res = client.get("/api/listings?location=Goa")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 2
    assert all(item["city"] == "Goa" for item in data["items"])

    res_manali = client.get("/api/listings?location=Manali")
    assert res_manali.status_code == 200
    assert res_manali.json()["total"] == 1
    assert res_manali.json()["items"][0]["city"] == "Manali"


def test_search_filter_by_category_and_property_type(client: TestClient, catalog_data):
    # Category
    res_cat = client.get("/api/listings?category=Beachfront")
    assert res_cat.json()["total"] == 1
    assert res_cat.json()["items"][0]["category"] == "Beachfront"

    # Property type
    res_prop = client.get("/api/listings?property_types=Villa")
    assert res_prop.json()["total"] == 1
    assert res_prop.json()["items"][0]["property_type"] == "Villa"


def test_search_filter_by_price_and_capacity(client: TestClient, catalog_data):
    # Price cents: l1 is 15000, l2 is 8000, l3 is 22000
    res_cheap = client.get("/api/listings?max_price_cents=10000")
    assert res_cheap.json()["total"] == 1
    assert res_cheap.json()["items"][0]["price_cents"] == 8000

    # Guests capacity
    res_guests = client.get("/api/listings?adults=5")
    assert res_guests.json()["total"] == 1
    assert res_guests.json()["items"][0]["max_guests"] >= 5


def test_search_filter_by_superhost(client: TestClient, catalog_data):
    res_super = client.get("/api/listings?superhost=true")
    assert res_super.status_code == 200
    assert res_super.json()["total"] == 2
    for item in res_super.json()["items"]:
        assert item["is_superhost"] is True


def test_search_filter_by_amenities_all_of(client: TestClient, catalog_data):
    # wifi + pool: l1 has both, l2 has wifi only, l3 has ac + pool
    a_wifi_id = catalog_data["a_wifi"].id
    a_pool_id = catalog_data["a_pool"].id

    res_both = client.get(f"/api/listings?amenity_ids={a_wifi_id}&amenity_ids={a_pool_id}")
    assert res_both.status_code == 200
    assert res_both.json()["total"] == 1
    assert res_both.json()["items"][0]["id"] == catalog_data["l1"].id


def test_search_date_exclusion_and_same_day_turnover(client: TestClient, catalog_data):
    # Listing 1 is booked 2026-11-05 to 2026-11-10
    l1_id = catalog_data["l1"].id

    # Overlapping dates: 2026-11-06 to 2026-11-08 -> Listing 1 must be excluded
    res_overlap = client.get("/api/listings?check_in=2026-11-06&check_out=2026-11-08&location=Goa")
    assert res_overlap.status_code == 200
    listing_ids = [item["id"] for item in res_overlap.json()["items"]]
    assert l1_id not in listing_ids

    # Adjacent checkout turnover: 2026-11-10 to 2026-11-14 -> Listing 1 is allowed
    res_after = client.get("/api/listings?check_in=2026-11-10&check_out=2026-11-14&location=Goa")
    assert res_after.status_code == 200
    listing_ids_after = [item["id"] for item in res_after.json()["items"]]
    assert l1_id in listing_ids_after

    # Adjacent checkin turnover: 2026-11-01 to 2026-11-05 -> Listing 1 is allowed
    res_before = client.get("/api/listings?check_in=2026-11-01&check_out=2026-11-05&location=Goa")
    assert res_before.status_code == 200
    listing_ids_before = [item["id"] for item in res_before.json()["items"]]
    assert l1_id in listing_ids_before


def test_search_date_validation_errors(client: TestClient, catalog_data):
    # Only check_in provided -> 422
    res1 = client.get("/api/listings?check_in=2026-11-05")
    assert res1.status_code == 422
    assert res1.json()["error"]["code"] == "VALIDATION_ERROR"

    # Only check_out provided -> 422
    res2 = client.get("/api/listings?check_out=2026-11-10")
    assert res2.status_code == 422
    assert res2.json()["error"]["code"] == "VALIDATION_ERROR"

    # Inverted dates: check_out <= check_in -> 422
    res3 = client.get("/api/listings?check_in=2026-11-10&check_out=2026-11-05")
    assert res3.status_code == 422
    assert res3.json()["error"]["code"] == "VALIDATION_ERROR"


def test_search_pagination_and_count_match(client: TestClient, catalog_data):
    # Page 1 of 2
    res_p1 = client.get("/api/listings?page=1&page_size=2")
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert len(data_p1["items"]) == 2
    assert data_p1["total"] == 3
    assert data_p1["has_more"] is True

    # Page 2 of 2
    res_p2 = client.get("/api/listings?page=2&page_size=2")
    assert res_p2.status_code == 200
    data_p2 = res_p2.json()
    assert len(data_p2["items"]) == 1
    assert data_p2["has_more"] is False

    # No duplicates or gaps
    ids_p1 = [item["id"] for item in data_p1["items"]]
    ids_p2 = [item["id"] for item in data_p2["items"]]
    assert set(ids_p1).isdisjoint(set(ids_p2))
    assert len(set(ids_p1 + ids_p2)) == 3

    # Total must exactly match count endpoint
    res_count = client.get("/api/listings/count")
    assert res_count.status_code == 200
    assert res_count.json()["total"] == data_p1["total"]


def test_facets_endpoint(client: TestClient, catalog_data):
    res = client.get("/api/listings/facets")
    assert res.status_code == 200
    facets = res.json()
    assert facets["price_min"] == 8000
    assert facets["price_max"] == 22000
    assert len(facets["histogram"]) == 20
    # Total count across histogram buckets equals total listings
    assert sum(b["count"] for b in facets["histogram"]) == 3


def test_listing_detail_and_soft_delete_404(client: TestClient, db_session: Session, catalog_data):
    l1 = catalog_data["l1"]
    res = client.get(f"/api/listings/{l1.id}")
    assert res.status_code == 200
    detail = res.json()
    assert detail["id"] == l1.id
    assert detail["title"] == l1.title
    assert len(detail["photos"]) == 2
    assert len(detail["amenities"]) == 2
    assert detail["host"]["is_superhost"] is True
    assert detail["guest_favorite"] is True  # rating >= 4.8 and count >= 5

    # Non-existent ID -> 404
    res_missing = client.get("/api/listings/999999")
    assert res_missing.status_code == 404
    assert res_missing.json()["error"]["code"] == "NOT_FOUND"

    # Soft-deleted listing -> 404
    l1.deleted_at = datetime.now(timezone.utc).isoformat()
    db_session.commit()
    res_deleted = client.get(f"/api/listings/{l1.id}")
    assert res_deleted.status_code == 404
    assert res_deleted.json()["error"]["code"] == "NOT_FOUND"


def test_listing_availability(client: TestClient, catalog_data):
    l1_id = catalog_data["l1"].id
    res = client.get(f"/api/listings/{l1_id}/availability")
    assert res.status_code == 200
    data = res.json()
    assert data["min_nights"] == 2
    assert len(data["booked"]) == 1
    assert data["booked"][0]["check_in"] == "2026-11-05"
    assert data["booked"][0]["check_out"] == "2026-11-10"


def test_listing_reviews(client: TestClient, catalog_data):
    l1_id = catalog_data["l1"].id
    res = client.get(f"/api/listings/{l1_id}/reviews")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1
    assert data["items"][0]["rating"] == 5.0
    assert data["summary"]["categories"]["cleanliness"] == 5.0
