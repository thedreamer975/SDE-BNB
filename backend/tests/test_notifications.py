from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.notification import Notification


def test_notifications_flow(client: TestClient, db_session: Session):
    # Register user
    reg = client.post(
        "/api/auth/register",
        json={"name": "Notif User", "email": "notifuser@example.com", "password": "Password123"},
    )
    user_id = reg.json()["id"]
    client.cookies.set("session", reg.cookies["session"])

    # Seed notifications for this user
    n1 = Notification(
        user_id=user_id,
        type="booking_confirmed",
        title="Booking confirmed",
        body="Your trip is booked!",
    )
    n2 = Notification(
        user_id=user_id,
        type="review_received",
        title="Leave a review",
        body="How was your stay?",
    )
    db_session.add_all([n1, n2])
    db_session.commit()

    # Get unread count
    res_count = client.get("/api/notifications/unread-count")
    assert res_count.status_code == 200
    assert res_count.json()["count"] == 2

    # List notifications
    res_list = client.get("/api/notifications")
    assert res_list.status_code == 200
    assert res_list.json()["total"] == 2
    assert len(res_list.json()["items"]) == 2

    # Mark one read
    res_read = client.post(f"/api/notifications/{n1.id}/read")
    assert res_read.status_code == 200
    assert res_read.json()["read_at"] is not None

    # Check unread count is 1
    res_count2 = client.get("/api/notifications/unread-count")
    assert res_count2.json()["count"] == 1

    # Mark all read
    res_all = client.post("/api/notifications/read-all")
    assert res_all.status_code == 200

    # Count is now 0
    res_count3 = client.get("/api/notifications/unread-count")
    assert res_count3.json()["count"] == 0
