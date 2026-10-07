from sqlalchemy import select, func
from app.db import SessionLocal
from app.models.user import User
from app.models.listing import Listing
from app.models.booking import Booking
from app.models.review import Review
from app.models.amenity import Amenity
from app.models.wishlist import WishlistItem
from app.models.notification import Notification
from app.services.pricing import calculate_quote


def test_seed_counts_and_demo_users():
    with SessionLocal() as db:
        user_count = db.scalar(select(func.count(User.id)))
        listing_count = db.scalar(select(func.count(Listing.id)))
        amenity_count = db.scalar(select(func.count(Amenity.id)))
        booking_count = db.scalar(select(func.count(Booking.id)))
        review_count = db.scalar(select(func.count(Review.id)))

        # Expectations per PRD §17
        assert user_count == 20
        assert listing_count == 36
        assert amenity_count == 30
        assert booking_count >= 30
        assert review_count >= 100

        # Verify demo guest
        guest = db.scalar(select(User).where(User.email == "guest@demo.com"))
        assert guest is not None
        assert guest.role == "guest"
        assert guest.name == "Alex Morgan"

        # Verify demo hosts and superhost flags
        host1 = db.scalar(select(User).where(User.email == "host@demo.com"))
        assert host1 is not None
        assert host1.role == "host"
        assert host1.is_superhost == 1

        host2 = db.scalar(select(User).where(User.email == "host2@demo.com"))
        assert host2 is not None
        assert host2.role == "host"
        assert host2.is_superhost == 1

        # Verify guest bookings
        guest_bookings = db.scalars(select(Booking).where(Booking.guest_id == guest.id)).all()
        assert len(guest_bookings) == 3
        statuses = [b.status for b in guest_bookings]
        assert "confirmed" in statuses
        assert "cancelled" in statuses

        # Verify wishlist items
        wishlists = db.scalars(select(WishlistItem).where(WishlistItem.user_id == guest.id)).all()
        assert len(wishlists) == 4

        # Verify notifications
        notifs = db.scalars(select(Notification).where(Notification.user_id == guest.id)).all()
        assert len(notifs) >= 2


def test_seed_listing_ratings():
    with SessionLocal() as db:
        listings = db.scalars(select(Listing)).all()
        assert len(listings) == 36

        top_rated = [listing for listing in listings if listing.rating_avg >= 4.8 and listing.rating_count >= 3]
        # PRD requirement: >= 10 listings with rating >= 4.8
        assert len(top_rated) >= 10

        new_listings = [listing for listing in listings if listing.rating_count == 0]
        # PRD requirement: 3 listings with 0 reviews ("New")
        assert len(new_listings) == 3


def test_seed_booking_pricing_math():
    with SessionLocal() as db:
        bookings = db.scalars(select(Booking)).all()
        assert len(bookings) > 0

        for b in bookings:
            assert b.total_cents == b.subtotal_cents + b.cleaning_cents + b.service_cents
            assert b.check_out > b.check_in


def test_no_confirmed_booking_overlaps():
    """
    Ensure no two confirmed bookings on the same listing overlap in dates.
    Same-day turnover (b1.check_out == b2.check_in) is permitted.
    """
    with SessionLocal() as db:
        listings = db.scalars(select(Listing)).all()
        for listing in listings:
            confirmed_bookings = db.scalars(
                select(Booking)
                .where(Booking.listing_id == listing.id, Booking.status == "confirmed")
                .order_by(Booking.check_in)
            ).all()

            for i in range(len(confirmed_bookings)):
                for j in range(i + 1, len(confirmed_bookings)):
                    b1 = confirmed_bookings[i]
                    b2 = confirmed_bookings[j]
                    # Overlap condition: b1.check_in < b2.check_out and b1.check_out > b2.check_in
                    overlaps = (b1.check_in < b2.check_out) and (b1.check_out > b2.check_in)
                    assert not overlaps, (
                        f"Overlap detected on listing {listing.id}: "
                        f"Booking {b1.code} ({b1.check_in} to {b1.check_out}) overlaps with "
                        f"Booking {b2.code} ({b2.check_in} to {b2.check_out})"
                    )


def test_pricing_quote_function():
    # 1 night test
    q1 = calculate_quote(listing_id=1, check_in="2026-11-01", check_out="2026-11-02", nightly_price_cents=10000, cleaning_fee_cents=2000)
    assert q1["nights"] == 1
    assert q1["subtotal_cents"] == 10000
    assert q1["cleaning_cents"] == 2000
    assert q1["service_cents"] == 1200  # 10000 * 0.12 = 1200
    assert q1["total_cents"] == 13200

    # 5 nights test with half-up rounding
    # nightly 14200 * 5 = 71000
    # service 71000 * 0.12 = 8520
    # cleaning 6000
    # total 71000 + 6000 + 8520 = 85520 (matches PRD §8.4 exact payload example!)
    q5 = calculate_quote(listing_id=12, check_in="2026-11-03", check_out="2026-11-08", nightly_price_cents=14200, cleaning_fee_cents=6000)
    assert q5["nights"] == 5
    assert q5["subtotal_cents"] == 71000
    assert q5["cleaning_cents"] == 6000
    assert q5["service_cents"] == 8520
    assert q5["total_cents"] == 85520
