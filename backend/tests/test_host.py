from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


def test_host_endpoints_flow(client: TestClient, db_session: Session):
    # Register host user
    reg = client.post(
        "/api/auth/register",
        json={"name": "Host Joe", "email": "hostjoe@example.com", "password": "Password123"},
    )
    client.cookies.set("session", reg.cookies["session"])

    # Become host
    become_host = client.post("/api/users/me/become-host")
    assert become_host.status_code == 200
    if "session" in become_host.cookies:
        client.cookies.set("session", become_host.cookies["session"])

    # Host summary initially empty
    summary = client.get("/api/host/summary")
    assert summary.status_code == 200
    assert summary.json()["total_listings"] == 0

    # Create listing
    create_res = client.post(
        "/api/host/listings",
        json={
            "title": "Joe's Mountain Retreat",
            "description": "Peaceful mountain retreat in the scenic hills with great panoramic views",
            "category": "Countryside",
            "property_type": "Cabin",
            "room_type": "entire_home",
            "address": "42 Pine Way",
            "city": "Shimla",
            "country": "India",
            "latitude": 31.1048,
            "longitude": 77.1734,
            "price_per_night": 15000,
            "cleaning_fee": 2500,
            "max_guests": 5,
            "bedrooms": 2,
            "beds": 3,
            "baths": 2.0,
            "photos": [
                {"url": "https://images.unsplash.com/photo-retreat1", "position": 1},
                {"url": "https://images.unsplash.com/photo-retreat2", "position": 2},
            ],
            "amenity_ids": [],
        },
    )
    assert create_res.status_code == 201
    listing_id = create_res.json()["id"]

    # Get host listings
    listings_res = client.get("/api/host/listings")
    assert listings_res.status_code == 200
    assert len(listings_res.json()) == 1

    # Update listing
    update_res = client.put(
        f"/api/host/listings/{listing_id}",
        json={
            "title": "Joe's Luxurious Mountain Retreat",
            "price_per_night": 18000,
        },
    )
    assert update_res.status_code == 200
    assert update_res.json()["price_per_night"] == 18000
    assert update_res.json()["title"] == "Joe's Luxurious Mountain Retreat"

    # Get reservations
    res_reservations = client.get("/api/host/reservations")
    assert res_reservations.status_code == 200

    # Delete listing
    delete_res = client.delete(f"/api/host/listings/{listing_id}")
    assert delete_res.status_code in (200, 204)

    # Confirm deleted
    listings_after = client.get("/api/host/listings")
    assert len(listings_after.json()) == 0
