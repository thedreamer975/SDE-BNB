import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.listing import Listing
from app.models.booking import Booking
from app.models.review import Review
from app.core.codes import generate_confirmation_code


def test_reject_duplicate_email(db_session: Session):
    u1 = User(
        name="User 1",
        email="test@demo.com",
        password_hash="hash1",
        role="guest",
    )
    db_session.add(u1)
    db_session.commit()

    u2 = User(
        name="User 2",
        email="test@demo.com",
        password_hash="hash2",
        role="guest",
    )
    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_reject_negative_price(db_session: Session):
    host = User(
        name="Host",
        email="host_neg@demo.com",
        password_hash="hash",
        role="host",
    )
    db_session.add(host)
    db_session.commit()

    listing = Listing(
        host_id=host.id,
        title="Invalid Price Listing",
        description="A great place with invalid price",
        category="Trending",
        property_type="House",
        room_type="entire_home",
        city="Goa",
        country="India",
        latitude=15.2,
        longitude=74.1,
        price_cents=-100,  # Negative!
        cleaning_fee_cents=0,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.5,
    )
    db_session.add(listing)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_reject_checkout_before_checkin(db_session: Session):
    host = User(name="Host", email="h1@demo.com", password_hash="h", role="host")
    guest = User(name="Guest", email="g1@demo.com", password_hash="h", role="guest")
    db_session.add_all([host, guest])
    db_session.commit()

    listing = Listing(
        host_id=host.id,
        title="Listing 1",
        description="Valid description here",
        category="Cabins",
        property_type="Cabin",
        room_type="entire_home",
        city="Manali",
        country="India",
        latitude=32.2,
        longitude=77.1,
        price_cents=10000,
        cleaning_fee_cents=1000,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.0,
    )
    db_session.add(listing)
    db_session.commit()

    # Invalid: check_out <= check_in
    b = Booking(
        code=generate_confirmation_code(),
        listing_id=listing.id,
        guest_id=guest.id,
        check_in="2026-11-10",
        check_out="2026-11-05",  # earlier than check_in!
        adults=2,
        nights=-5,
        nightly_cents=10000,
        subtotal_cents=-50000,
        cleaning_cents=1000,
        service_cents=-6000,
        total_cents=-55000,
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(b)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_reject_total_math_mismatch(db_session: Session):
    host = User(name="Host", email="h2@demo.com", password_hash="h", role="host")
    guest = User(name="Guest", email="g2@demo.com", password_hash="h", role="guest")
    db_session.add_all([host, guest])
    db_session.commit()

    listing = Listing(
        host_id=host.id,
        title="Listing 2",
        description="Valid description here",
        category="Cabins",
        property_type="Cabin",
        room_type="entire_home",
        city="Manali",
        country="India",
        latitude=32.2,
        longitude=77.1,
        price_cents=10000,
        cleaning_fee_cents=1000,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.0,
    )
    db_session.add(listing)
    db_session.commit()

    # total_cents does not equal subtotal + cleaning + service
    b = Booking(
        code=generate_confirmation_code(),
        listing_id=listing.id,
        guest_id=guest.id,
        check_in="2026-11-01",
        check_out="2026-11-04",
        adults=2,
        nights=3,
        nightly_cents=10000,
        subtotal_cents=30000,
        cleaning_cents=1000,
        service_cents=3600,
        total_cents=99999,  # Mismatched! Expected 34600
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(b)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_reject_bad_review_rating(db_session: Session):
    host = User(name="Host", email="h3@demo.com", password_hash="h", role="host")
    guest = User(name="Guest", email="g3@demo.com", password_hash="h", role="guest")
    db_session.add_all([host, guest])
    db_session.commit()

    listing = Listing(
        host_id=host.id,
        title="Listing 3",
        description="Valid description here",
        category="Cabins",
        property_type="Cabin",
        room_type="entire_home",
        city="Manali",
        country="India",
        latitude=32.2,
        longitude=77.1,
        price_cents=10000,
        cleaning_fee_cents=1000,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.0,
    )
    db_session.add(listing)
    db_session.commit()

    b = Booking(
        code=generate_confirmation_code(),
        listing_id=listing.id,
        guest_id=guest.id,
        check_in="2026-09-01",
        check_out="2026-09-04",
        adults=2,
        nights=3,
        nightly_cents=10000,
        subtotal_cents=30000,
        cleaning_cents=1000,
        service_cents=3600,
        total_cents=34600,
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(b)
    db_session.commit()

    # Sub-score of 6 is invalid (CHECK between 1 and 5)
    r = Review(
        booking_id=b.id,
        listing_id=listing.id,
        author_id=guest.id,
        cleanliness=6,  # Invalid!
        accuracy=5,
        communication=5,
        location=5,
        check_in_rating=5,
        value=5,
        rating=5.0,
        comment="Exceeded expectations, 10 out of 10!",
    )
    db_session.add(r)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()


def test_foreign_key_enforcement(db_session: Session):
    # Booking with non-existent listing_id should fail when FKs are enforced
    b = Booking(
        code=generate_confirmation_code(),
        listing_id=999999,  # Non-existent
        guest_id=999999,
        check_in="2026-11-01",
        check_out="2026-11-04",
        adults=2,
        nights=3,
        nightly_cents=10000,
        subtotal_cents=30000,
        cleaning_cents=1000,
        service_cents=3600,
        total_cents=34600,
        status="confirmed",
        payment_status="paid",
    )
    db_session.add(b)
    with pytest.raises(IntegrityError):
        db_session.commit()
    db_session.rollback()
