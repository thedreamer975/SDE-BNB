from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.listing import Listing, ListingPhoto
from app.models.user import User


def test_bookings_and_quote_flow(client: TestClient, db_session: Session):
    # 1. Create host and listing
    host = User(name="Host Person", email="hostperson@demo.com", password_hash="dummy", role="host")
    guest = User(name="Guest Person", email="guestperson@demo.com", password_hash="dummy", role="guest")
    db_session.add_all([host, guest])
    db_session.commit()

    listing = Listing(
        host_id=host.id,
        title="Cozy Cottage",
        description="A great place to stay",
        category="Countryside",
        property_type="House",
        room_type="entire_home",
        address_line="123 Country Rd",
        city="Manali",
        country="India",
        latitude=32.24,
        longitude=77.18,
        price_cents=10000,
        cleaning_fee_cents=1500,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.0,
    )
    listing.photos = [
        ListingPhoto(url="https://images.unsplash.com/photo1", position=1, alt="Cottage"),
    ]
    db_session.add(listing)
    db_session.commit()

    # 2. Login as guest
    login_res = client.post(
        "/api/auth/register",
        json={"name": "Booker User", "email": "booker@example.com", "password": "Password123"},
    )
    client.cookies.set("session", login_res.cookies["session"])

    today = date.today()
    d1 = (today + timedelta(days=10)).isoformat()
    d2 = (today + timedelta(days=13)).isoformat()

    # Quote check
    quote_res = client.post(
        f"/api/listings/{listing.id}/quote",
        json={"check_in": d1, "check_out": d2, "adults": 2, "children": 0, "infants": 0, "pets": 0},
    )
    assert quote_res.status_code == 200
    qdata = quote_res.json()
    assert qdata["nights"] == 3
    assert qdata["price_per_night"] == 10000
    assert qdata["nightly_total"] == 30000
    assert qdata["cleaning_fee"] == 1500
    assert qdata["total"] > 31500

    # Book listing
    book_res = client.post(
        "/api/bookings",
        json={
            "listing_id": listing.id,
            "check_in": d1,
            "check_out": d2,
            "adults": 2,
            "children": 0,
            "infants": 0,
            "pets": 0,
            "payment_token": "tok_visa_valid",
        },
    )
    assert book_res.status_code == 201
    bdata = book_res.json()
    assert bdata["listing_id"] == str(listing.id)
    assert bdata["status"] == "confirmed"
    assert bdata["confirmation_code"].startswith("HM")
    booking_id = bdata["id"]

    # Attempt overlap booking -> 409
    overlap_res = client.post(
        "/api/bookings",
        json={
            "listing_id": listing.id,
            "check_in": d1,
            "check_out": d2,
            "adults": 1,
            "children": 0,
            "infants": 0,
            "pets": 0,
            "payment_token": "tok_visa_valid",
        },
    )
    assert overlap_res.status_code == 409

    # Check my bookings
    my_bookings = client.get("/api/bookings/me")
    assert my_bookings.status_code == 200
    assert len(my_bookings.json()["bookings"]) >= 1

    # Check cancel preview
    cancel_prev = client.get(f"/api/bookings/{booking_id}/cancel-preview")
    assert cancel_prev.status_code == 200
    assert "refund_amount" in cancel_prev.json()

    # Cancel booking
    cancel_res = client.post(f"/api/bookings/{booking_id}/cancel")
    assert cancel_res.status_code == 200
    assert cancel_res.json()["status"] == "cancelled"
