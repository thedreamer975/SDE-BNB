# ruff: noqa: E402
import argparse
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure backend directory is first in sys.path and remove script directory to avoid shadowing
backend_dir = Path(__file__).resolve().parent.parent
seed_dir = Path(__file__).resolve().parent
if str(seed_dir) in sys.path:
    sys.path.remove(str(seed_dir))
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from sqlalchemy import select, func
from app.db import Base, engine, SessionLocal, init_db
from app.models.user import User
from app.models.amenity import Amenity
from app.models.listing import Listing, ListingPhoto
from app.models.booking import Booking
from app.models.review import Review
from app.models.wishlist import WishlistItem
from app.models.notification import Notification
from app.core.codes import generate_confirmation_code
from app.core.dates import get_server_today, parse_date, format_date
from app.services.pricing import calculate_quote
from app.security import hash_password
from seed.data import (
    AMENITIES_DATA,
    DESTINATIONS_DATA,
    CATEGORIES,
    PROPERTY_TYPES,
    ROOM_TYPES,
    UNSPLASH_PHOTO_IDS,
    REVIEW_COMMENTS_HIGH,
    REVIEW_COMMENTS_MID,
)


def seed_database(reset: bool = False) -> None:
    # Deterministic seed for reproducible testing
    random.seed(42)

    if reset:
        print("Reset flag passed: dropping and recreating all tables...")
        Base.metadata.drop_all(bind=engine)
        init_db(engine)
    else:
        init_db(engine)
        with SessionLocal() as db:
            existing_users = db.scalar(select(func.count(User.id)))
            if existing_users and existing_users > 0:
                print("Database already contains data. Idempotent skip.")
                return

    print("Beginning database seeding...")
    with SessionLocal() as db:
        # 1. Amenities
        amenities = []
        for a_data in AMENITIES_DATA:
            amenity = Amenity(
                name=a_data["name"],
                icon_key=a_data["icon_key"],
                group=a_data["group"],
            )
            db.add(amenity)
            amenities.append(amenity)
        db.flush()
        print(f"Seeded {len(amenities)} amenities.")

        # 2. Users
        demo_password_hash = hash_password("Demo1234")

        # Demo guest
        guest_demo = User(
            name="Alex Morgan",
            email="guest@demo.com",
            password_hash=demo_password_hash,
            role="guest",
            avatar_url="https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=400&q=80",
            bio="Design enthusiast and weekend explorer.",
        )
        db.add(guest_demo)

        # Demo host 1
        host_demo1 = User(
            name="Priya Sharma",
            email="host@demo.com",
            password_hash=demo_password_hash,
            role="host",
            avatar_url="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=400&q=80",
            bio="Architect and superhost passionate about sustainable stays.",
            is_superhost=1,
        )
        db.add(host_demo1)

        # Demo host 2
        host_demo2 = User(
            name="Marco Rossi",
            email="host2@demo.com",
            password_hash=demo_password_hash,
            role="host",
            avatar_url="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=400&q=80",
            bio="Chef and villa host in the Mediterranean and beyond.",
            is_superhost=1,
        )
        db.add(host_demo2)

        # 5 more hosts (12 listings between them)
        other_hosts_meta = [
            ("Elena Gomez", "host3@demo.com"),
            ("David Kim", "host4@demo.com"),
            ("Sophie Martin", "host5@demo.com"),
            ("Lucas Silva", "host6@demo.com"),
            ("Aisha Patel", "host7@demo.com"),
        ]
        other_hosts = []
        for name, email in other_hosts_meta:
            h = User(
                name=name,
                email=email,
                password_hash=demo_password_hash,
                role="host",
                avatar_url="https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=400&q=80",
            )
            db.add(h)
            other_hosts.append(h)

        # 12 reviewer guests
        reviewers = []
        for i in range(1, 13):
            r = User(
                name=f"Traveler {i}",
                email=f"reviewer{i}@demo.com",
                password_hash=demo_password_hash,
                role="guest",
            )
            db.add(r)
            reviewers.append(r)

        db.flush()
        all_hosts = [host_demo1, host_demo2] + other_hosts
        print(f"Seeded {len(all_hosts) + len(reviewers) + 1} users.")

        # 3. Listings (36 total: 12 destinations × 3)
        # Distribute host ownership: host1 gets 14 listings, host2 gets 10, other 5 get 12 (approx 2-3 each)
        host_assignments = [host_demo1] * 14 + [host_demo2] * 10
        # remaining 12 listings across the 5 other hosts
        for i in range(12):
            host_assignments.append(other_hosts[i % len(other_hosts)])
        random.shuffle(host_assignments)

        listings = []
        photo_idx = 0
        listing_counter = 0

        # Predefined listing title templates
        titles_pool = [
            "Serene Seaside Villa with Sunset Terrace",
            "Cozy Alpine Chalet with Wood-Fired Sauna",
            "Modern Heritage Haveli with Courtyard Pool",
            "Chic Sunlight Loft in Historic Old Town",
            "Bamboo Sanctuary with Jungle Infinity Pool",
            "Mountain Pine Lodge with Stargazing Deck",
            "Whitewashed Cliffside Suite with Caldera Views",
            "Zen Garden Machiya with Cypress Onsen Bath",
            "Oceanfront Panoramic Penthouse & Rooftop Lounge",
            "Boho Eco-Chic Beachfront Bungalow",
            "Historic Tuscan Stone Farmhouse & Vineyard",
            "Glacier View Wilderness Cabin with Hot Tub",
        ]

        # Ensure all 14 categories appear at least 2 times across the 36 listings
        assigned_categories = []
        for cat in CATEGORIES:
            assigned_categories.extend([cat, cat])  # 28
        while len(assigned_categories) < 36:
            assigned_categories.append(random.choice(CATEGORIES))
        random.shuffle(assigned_categories)

        for dest_idx, dest in enumerate(DESTINATIONS_DATA):
            for var in range(3):
                category = assigned_categories[listing_counter]
                host = host_assignments[listing_counter]
                prop_type = random.choice(PROPERTY_TYPES)
                room_type = "entire_home" if var != 2 else random.choice(ROOM_TYPES)

                # Random price $45-$520
                price_cents = random.randint(45, 520) * 100
                cleaning_fee_cents = random.choice([0, 30, 50, 75, 120]) * 100
                max_guests = random.randint(2, 10)
                bedrooms = random.randint(1, 5) if room_type != "private_room" else 1
                beds = max(bedrooms, random.randint(1, 6))
                baths = float(random.choice([1, 1.5, 2, 2.5, 3]))

                # Slightly jitter lat/lng
                lat_jitter = dest["lat"] + (random.random() - 0.5) * 0.04
                lng_jitter = dest["lng"] + (random.random() - 0.5) * 0.04

                base_title = titles_pool[dest_idx % len(titles_pool)]
                title = f"{base_title} #{var+1}" if var > 0 else base_title
                desc = (
                    f"Welcome to your sanctuary in {dest['city']}, {dest['country']}. "
                    f"This extraordinary {prop_type.lower()} combines architectural character with thoughtful comforts. "
                    "Features bright airy interiors, premium organic bedding, curated artisan furniture, and high-speed connectivity. "
                    "Unwind on the private patio or explore vibrant local cafes and scenic trails just minutes away."
                )

                listing = Listing(
                    host_id=host.id,
                    title=title,
                    description=desc,
                    category=category,
                    property_type=prop_type,
                    room_type=room_type,
                    address_line=f"{random.randint(12, 888)} Heritage Way",
                    city=dest["city"],
                    country=dest["country"],
                    latitude=round(lat_jitter, 5),
                    longitude=round(lng_jitter, 5),
                    price_cents=price_cents,
                    cleaning_fee_cents=cleaning_fee_cents,
                    max_guests=max_guests,
                    bedrooms=bedrooms,
                    beds=beds,
                    baths=baths,
                    pets_allowed=1 if random.random() > 0.4 else 0,
                    check_in_time="15:00",
                    check_out_time="11:00",
                    min_nights=random.choice([1, 2, 3]),
                    max_nights=30,
                    house_rules="Quiet hours after 10 PM. Please remove shoes inside. Enjoy and relax!",
                )

                # Assign 6-14 amenities
                num_amenities = random.randint(8, 16)
                chosen_amenities = random.sample(amenities, min(num_amenities, len(amenities)))
                listing.amenities = chosen_amenities

                db.add(listing)
                db.flush()

                # Add 5 photos
                for p_pos in range(1, 6):
                    p_id = UNSPLASH_PHOTO_IDS[(photo_idx + p_pos) % len(UNSPLASH_PHOTO_IDS)]
                    url = f"https://images.unsplash.com/photo-{p_id}?auto=format&fit=crop&w=1400&q=80"
                    photo = ListingPhoto(
                        listing_id=listing.id,
                        url=url,
                        position=p_pos,
                        alt=f"{title} - view {p_pos}",
                    )
                    db.add(photo)

                photo_idx += 5
                listing_counter += 1
                listings.append(listing)

        db.flush()
        print(f"Seeded {len(listings)} listings with 5 photos each.")

        # 4. Bookings & Reviews
        # Base today date
        today_date = parse_date(get_server_today())

        all_bookings = []
        all_reviews = []

        # 3 listings with 0 reviews ("New") per PRD §17
        unreviewed_listing_indices = {0, 1, 2}

        # Seed bookings per listing
        for idx, listing in enumerate(listings):
            # For listings that will have reviews, create 3 to 6 past bookings
            if idx not in unreviewed_listing_indices:
                num_reviews = random.randint(3, 7)
                review_ratings = []

                # Build non-overlapping past bookings by walking BACKWARDS from
                # a cursor well before today, stacking into the deeper past.
                # Start the cursor 10 days before today so all checkout dates
                # are strictly in the past.
                cursor_date = today_date - timedelta(days=10)

                # Pre-calculate each booking's nights + gap to lay them out
                booking_specs = []
                for _ in range(num_reviews):
                    b_nights = random.randint(2, 5)
                    gap_after = random.randint(3, 10)
                    booking_specs.append((b_nights, gap_after))

                # Walk backward from cursor_date to place bookings
                # (most recent booking first, then further into the past)
                booking_dates = []
                cur = cursor_date
                for b_nights, gap_after in booking_specs:
                    b_checkout = cur
                    b_checkin = b_checkout - timedelta(days=b_nights)
                    booking_dates.append((b_checkin, b_checkout))
                    cur = b_checkin - timedelta(days=gap_after)

                # Reverse so bookings are chronological (oldest first)
                booking_dates.reverse()

                for r_idx, (b_checkin, b_checkout) in enumerate(booking_dates):
                    quote = calculate_quote(
                        listing.id,
                        format_date(b_checkin),
                        format_date(b_checkout),
                        listing.price_cents,
                        listing.cleaning_fee_cents,
                    )

                    author = reviewers[r_idx % len(reviewers)]
                    booking = Booking(
                        code=generate_confirmation_code(),
                        listing_id=listing.id,
                        guest_id=author.id,
                        check_in=quote["check_in"],
                        check_out=quote["check_out"],
                        adults=random.randint(1, min(4, listing.max_guests)),
                        nights=quote["nights"],
                        nightly_cents=quote["nightly_cents"],
                        subtotal_cents=quote["subtotal_cents"],
                        cleaning_cents=quote["cleaning_cents"],
                        service_cents=quote["service_cents"],
                        total_cents=quote["total_cents"],
                        status="confirmed",
                        payment_status="paid",
                        payment_brand="visa",
                        payment_last4="4242",
                        listing_title_snapshot=listing.title,
                        listing_cover_snapshot=listing.photos[0].url if listing.photos else None,
                    )
                    db.add(booking)
                    db.flush()
                    all_bookings.append(booking)

                    # Create review for past booking
                    # High ratings for first 16 listings (indices 3-15 after skipping
                    # 0-2 unreviewed) so we get >= 10 listings with rating >= 4.8
                    is_top_rated = idx < 16  # indices 3-15 = 13 reviewed listings
                    if is_top_rated:
                        # Force high: all 5s with rare 4, guaranteeing avg >= 4.83
                        subscores = [5, 5, 5, 5, 5, random.choice([5, 5, 4])]
                        comment = random.choice(REVIEW_COMMENTS_HIGH)
                    else:
                        subscores = [random.choice([4, 4, 5, 3]) for _ in range(6)]
                        comment = random.choice(REVIEW_COMMENTS_MID)

                    review_score = round(sum(subscores) / 6.0, 2)
                    review_ratings.append(review_score)

                    rev = Review(
                        booking_id=booking.id,
                        listing_id=listing.id,
                        author_id=author.id,
                        cleanliness=subscores[0],
                        accuracy=subscores[1],
                        communication=subscores[2],
                        location=subscores[3],
                        check_in_rating=subscores[4],
                        value=subscores[5],
                        rating=review_score,
                        comment=comment,
                    )
                    db.add(rev)
                    all_reviews.append(rev)

                # Update listing rating aggregates
                listing.rating_count = len(review_ratings)
                listing.rating_avg = round(sum(review_ratings) / len(review_ratings), 2)

        # Demo guest specific bookings (PRD §17: 1 upcoming, 1 past unreviewed, 1 cancelled)
        target_listing1 = listings[3]
        target_listing2 = listings[4]
        target_listing3 = listings[5]

        # 1 upcoming for guest@demo.com
        up_in = today_date + timedelta(days=12)
        up_out = up_in + timedelta(days=4)
        up_quote = calculate_quote(
            target_listing1.id,
            format_date(up_in),
            format_date(up_out),
            target_listing1.price_cents,
            target_listing1.cleaning_fee_cents,
        )
        b_up = Booking(
            code=generate_confirmation_code(),
            listing_id=target_listing1.id,
            guest_id=guest_demo.id,
            check_in=up_quote["check_in"],
            check_out=up_quote["check_out"],
            adults=2,
            nights=up_quote["nights"],
            nightly_cents=up_quote["nightly_cents"],
            subtotal_cents=up_quote["subtotal_cents"],
            cleaning_cents=up_quote["cleaning_cents"],
            service_cents=up_quote["service_cents"],
            total_cents=up_quote["total_cents"],
            status="confirmed",
            payment_status="paid",
            payment_brand="visa",
            payment_last4="4242",
            listing_title_snapshot=target_listing1.title,
            listing_cover_snapshot=target_listing1.photos[0].url,
        )
        db.add(b_up)
        all_bookings.append(b_up)

        # Back-to-back same-day turnover booking on target_listing1 (checkout day = checkin day of next booking)
        b2b_in = up_out
        b2b_out = b2b_in + timedelta(days=3)
        b2b_quote = calculate_quote(
            target_listing1.id,
            format_date(b2b_in),
            format_date(b2b_out),
            target_listing1.price_cents,
            target_listing1.cleaning_fee_cents,
        )
        b_b2b = Booking(
            code=generate_confirmation_code(),
            listing_id=target_listing1.id,
            guest_id=reviewers[0].id,
            check_in=b2b_quote["check_in"],
            check_out=b2b_quote["check_out"],
            adults=2,
            nights=b2b_quote["nights"],
            nightly_cents=b2b_quote["nightly_cents"],
            subtotal_cents=b2b_quote["subtotal_cents"],
            cleaning_cents=b2b_quote["cleaning_cents"],
            service_cents=b2b_quote["service_cents"],
            total_cents=b2b_quote["total_cents"],
            status="confirmed",
            payment_status="paid",
            payment_brand="mastercard",
            payment_last4="8821",
            listing_title_snapshot=target_listing1.title,
            listing_cover_snapshot=target_listing1.photos[0].url,
        )
        db.add(b_b2b)
        all_bookings.append(b_b2b)

        # 1 past unreviewed for guest@demo.com (can be reviewed in S10)
        past_in = today_date - timedelta(days=10)
        past_out = past_in + timedelta(days=3)
        past_quote = calculate_quote(
            target_listing2.id,
            format_date(past_in),
            format_date(past_out),
            target_listing2.price_cents,
            target_listing2.cleaning_fee_cents,
        )
        b_past = Booking(
            code=generate_confirmation_code(),
            listing_id=target_listing2.id,
            guest_id=guest_demo.id,
            check_in=past_quote["check_in"],
            check_out=past_quote["check_out"],
            adults=1,
            nights=past_quote["nights"],
            nightly_cents=past_quote["nightly_cents"],
            subtotal_cents=past_quote["subtotal_cents"],
            cleaning_cents=past_quote["cleaning_cents"],
            service_cents=past_quote["service_cents"],
            total_cents=past_quote["total_cents"],
            status="confirmed",
            payment_status="paid",
            payment_brand="visa",
            payment_last4="4242",
            listing_title_snapshot=target_listing2.title,
            listing_cover_snapshot=target_listing2.photos[0].url,
        )
        db.add(b_past)
        all_bookings.append(b_past)

        # 1 cancelled booking for guest@demo.com
        canc_in = today_date + timedelta(days=25)
        canc_out = canc_in + timedelta(days=3)
        canc_quote = calculate_quote(
            target_listing3.id,
            format_date(canc_in),
            format_date(canc_out),
            target_listing3.price_cents,
            target_listing3.cleaning_fee_cents,
        )
        b_canc = Booking(
            code=generate_confirmation_code(),
            listing_id=target_listing3.id,
            guest_id=guest_demo.id,
            check_in=canc_quote["check_in"],
            check_out=canc_quote["check_out"],
            adults=2,
            nights=canc_quote["nights"],
            nightly_cents=canc_quote["nightly_cents"],
            subtotal_cents=canc_quote["subtotal_cents"],
            cleaning_cents=canc_quote["cleaning_cents"],
            service_cents=canc_quote["service_cents"],
            total_cents=canc_quote["total_cents"],
            status="cancelled",
            payment_status="refunded",
            refund_cents=canc_quote["total_cents"],
            cancelled_at=(today_date - timedelta(days=1)).isoformat(),
            payment_brand="visa",
            payment_last4="4242",
            listing_title_snapshot=target_listing3.title,
            listing_cover_snapshot=target_listing3.photos[0].url,
        )
        db.add(b_canc)
        all_bookings.append(b_canc)

        # Add more upcoming bookings across listings
        for idx in range(6, 18):
            target_listing = listings[idx]
            u_in = today_date + timedelta(days=random.randint(5, 60))
            u_out = u_in + timedelta(days=random.randint(2, 5))
            u_quote = calculate_quote(
                target_listing.id,
                format_date(u_in),
                format_date(u_out),
                target_listing.price_cents,
                target_listing.cleaning_fee_cents,
            )
            g = reviewers[idx % len(reviewers)]
            b_item = Booking(
                code=generate_confirmation_code(),
                listing_id=target_listing.id,
                guest_id=g.id,
                check_in=u_quote["check_in"],
                check_out=u_quote["check_out"],
                adults=2,
                nights=u_quote["nights"],
                nightly_cents=u_quote["nightly_cents"],
                subtotal_cents=u_quote["subtotal_cents"],
                cleaning_cents=u_quote["cleaning_cents"],
                service_cents=u_quote["service_cents"],
                total_cents=u_quote["total_cents"],
                status="confirmed",
                payment_status="paid",
                payment_brand="amex",
                payment_last4="1005",
                listing_title_snapshot=target_listing.title,
                listing_cover_snapshot=target_listing.photos[0].url if target_listing.photos else None,
            )
            db.add(b_item)
            all_bookings.append(b_item)

        # 5. Wishlists (guest@demo.com has 4 wishlist items)
        for w_idx in [0, 4, 8, 12]:
            w_item = WishlistItem(
                user_id=guest_demo.id,
                listing_id=listings[w_idx].id,
            )
            db.add(w_item)

        # 6. Notifications for demo users
        notifs_data = [
            (
                guest_demo.id,
                "booking_confirmed",
                "Reservation Confirmed!",
                f"Your reservation for {target_listing1.title} is confirmed.",
                f"/trips/{b_up.id}",
                None,
            ),
            (
                guest_demo.id,
                "booking_cancelled",
                "Reservation Cancelled",
                f"Your reservation for {target_listing3.title} was cancelled and refunded.",
                f"/trips/{b_canc.id}",
                (datetime.now() - timedelta(hours=5)).isoformat(),
            ),
            (
                host_demo1.id,
                "booking_received",
                "New Booking Received!",
                f"Alex Morgan booked {target_listing1.title}.",
                "/hosting/reservations",
                None,
            ),
            (
                host_demo1.id,
                "review_received",
                "New 5-Star Review!",
                "A guest left you a new review.",
                "/hosting",
                (datetime.now() - timedelta(days=2)).isoformat(),
            ),
        ]
        for u_id, n_type, n_title, n_body, n_link, n_read in notifs_data:
            notif = Notification(
                user_id=u_id,
                type=n_type,
                title=n_title,
                body=n_body,
                link=n_link,
                read_at=n_read,
            )
            db.add(notif)

        db.commit()

        print("Database successfully seeded!")
        print(f"Total Listings: {len(listings)}")
        print(f"Total Bookings: {len(all_bookings)}")
        print(f"Total Reviews: {len(all_reviews)}")


def main():
    parser = argparse.ArgumentParser(description="Seed the Airbnb clone database.")
    parser.add_argument("--reset", action="store_true", help="Reset all tables before seeding")
    args = parser.parse_args()
    seed_database(reset=args.reset)


if __name__ == "__main__":
    main()
