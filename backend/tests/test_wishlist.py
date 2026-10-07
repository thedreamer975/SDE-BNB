from datetime import datetime, timezone
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.listing import Listing, ListingPhoto
from app.models.user import User


def test_wishlist_unauthenticated_rejected(client: TestClient):
    assert client.get("/api/wishlist").status_code == 401
    assert client.get("/api/wishlist/ids").status_code == 401
    assert client.put("/api/wishlist/1").status_code == 401
    assert client.delete("/api/wishlist/1").status_code == 401


def test_wishlist_add_and_remove_idempotent(client: TestClient, db_session: Session):
    # 1. Register user
    reg = client.post(
        "/api/auth/register",
        json={"name": "Wishlist User", "email": "wish@example.com", "password": "Password123"},
    )
    cookie = reg.cookies["session"]
    client.cookies.set("session", cookie)

    # 2. Seed a listing
    host = User(name="Host", email="whost@demo.com", password_hash="dummy", role="host")
    db_session.add(host)
    db_session.flush()

    listing = Listing(
        host_id=host.id,
        title="Wishlist Test Villa",
        description="Beautiful villa",
        category="Beachfront",
        property_type="Villa",
        room_type="entire_home",
        address_line="10 Ocean Ave",
        city="Goa",
        country="India",
        latitude=15.2,
        longitude=74.1,
        price_cents=12000,
        cleaning_fee_cents=2000,
        max_guests=4,
        bedrooms=2,
        beds=2,
        baths=1.5,
    )
    listing.photos = [
        ListingPhoto(url="https://images.unsplash.com/wish1", position=1, alt="Photo"),
    ]
    db_session.add(listing)
    db_session.commit()

    # Initially not saved
    res_ids_init = client.get("/api/wishlist/ids")
    assert res_ids_init.status_code == 200
    assert res_ids_init.json() == []

    res_card_init = client.get(f"/api/listings/{listing.id}")
    assert res_card_init.json()["saved"] is False

    # 3. Add to wishlist
    res_add1 = client.put(f"/api/wishlist/{listing.id}")
    assert res_add1.status_code == 204

    # 4. Add again (idempotent)
    res_add2 = client.put(f"/api/wishlist/{listing.id}")
    assert res_add2.status_code == 204

    # 5. Verify saved
    res_ids = client.get("/api/wishlist/ids")
    assert res_ids.json() == [listing.id]

    res_list = client.get("/api/wishlist")
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1
    assert res_list.json()[0]["id"] == listing.id
    assert res_list.json()[0]["saved"] is True

    res_card = client.get(f"/api/listings/{listing.id}")
    assert res_card.json()["saved"] is True

    # 6. Remove from wishlist
    res_del1 = client.delete(f"/api/wishlist/{listing.id}")
    assert res_del1.status_code == 204

    # 7. Remove again (idempotent)
    res_del2 = client.delete(f"/api/wishlist/{listing.id}")
    assert res_del2.status_code == 204

    # 8. Verify no longer saved
    assert client.get("/api/wishlist/ids").json() == []
    assert client.get("/api/wishlist").json() == []
    assert client.get(f"/api/listings/{listing.id}").json()["saved"] is False


def test_wishlist_nonexistent_and_soft_deleted(client: TestClient, db_session: Session):
    reg = client.post(
        "/api/auth/register",
        json={"name": "Wishlist User 2", "email": "wish2@example.com", "password": "Password123"},
    )
    client.cookies.set("session", reg.cookies["session"])

    # Non-existent listing
    res_404 = client.put("/api/wishlist/999999")
    assert res_404.status_code == 404
    assert res_404.json()["error"]["code"] == "NOT_FOUND"

    # Add valid listing, then soft-delete it
    host = User(name="Host", email="whost2@demo.com", password_hash="dummy", role="host")
    db_session.add(host)
    db_session.flush()

    listing = Listing(
        host_id=host.id,
        title="Will Be Deleted",
        description="Desc",
        category="Trending",
        property_type="House",
        room_type="entire_home",
        address_line="Street",
        city="City",
        country="Country",
        latitude=10.0,
        longitude=10.0,
        price_cents=10000,
        cleaning_fee_cents=1000,
        max_guests=2,
        bedrooms=1,
        beds=1,
        baths=1.0,
    )
    db_session.add(listing)
    db_session.commit()

    # Add to wishlist
    assert client.put(f"/api/wishlist/{listing.id}").status_code == 204
    assert client.get("/api/wishlist/ids").json() == [listing.id]

    # Soft delete listing
    listing.deleted_at = datetime.now(timezone.utc).isoformat()
    db_session.commit()

    # Wishlist query should omit the soft-deleted listing
    assert client.get("/api/wishlist").json() == []
    assert client.get("/api/wishlist/ids").json() == []
