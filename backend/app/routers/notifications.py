"""
Notifications router: list, mark read, mark all read.
"""
from typing import Annotated
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, and_, update
from sqlalchemy.orm import Session

from app.db import get_db
from app.deps import get_current_user
from app.errors import NotFoundError
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime, timezone

router = APIRouter(tags=["Notifications"])

DbDep = Annotated[Session, Depends(get_db)]
UserDep = Annotated[User, Depends(get_current_user)]


def _serialize_notification(n: Notification) -> dict:
    return {
        "id": str(n.id),
        "type": n.type,
        "title": n.title,
        "body": n.body,
        "link": n.link,
        "read_at": n.read_at,
        "created_at": n.created_at,
    }


@router.get("/notifications")
def list_notifications(
    db: DbDep,
    user: UserDep,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
):
    """List user's notifications, newest first."""
    offset = (page - 1) * page_size
    total = db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == user.id)
    ).scalar_one() or 0
    unread = db.execute(
        select(func.count(Notification.id)).where(
            and_(Notification.user_id == user.id, Notification.read_at.is_(None))
        )
    ).scalar_one() or 0

    items = db.execute(
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .offset(offset)
        .limit(page_size)
    ).scalars().all()

    return {
        "items": [_serialize_notification(n) for n in items],
        "total": total,
        "unread": unread,
        "page": page,
        "page_size": page_size,
    }


@router.get("/notifications/unread-count")
def get_unread_count(db: DbDep, user: UserDep):
    """Quick check of unread notification count for the bell badge."""
    count = db.execute(
        select(func.count(Notification.id)).where(
            and_(Notification.user_id == user.id, Notification.read_at.is_(None))
        )
    ).scalar_one() or 0
    return {"count": count}


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: str, db: DbDep, user: UserDep):
    """Mark a single notification as read."""
    notif = db.get(Notification, int(notification_id))
    if not notif or notif.user_id != user.id:
        raise NotFoundError("Notification not found.")
    if notif.read_at is None:
        notif.read_at = datetime.now(timezone.utc).isoformat()
        db.commit()
    return _serialize_notification(notif)


@router.post("/notifications/read-all")
def mark_all_read(db: DbDep, user: UserDep):
    """Mark all of the user's unread notifications as read."""
    now = datetime.now(timezone.utc).isoformat()
    db.execute(
        update(Notification)
        .where(and_(Notification.user_id == user.id, Notification.read_at.is_(None)))
        .values(read_at=now)
    )
    db.commit()
    return {"status": "ok"}
