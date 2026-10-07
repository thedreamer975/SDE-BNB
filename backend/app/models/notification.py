from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlalchemy import (
    CheckConstraint,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

if TYPE_CHECKING:
    from app.models.user import User


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "type IN ('booking_confirmed', 'booking_received', 'booking_cancelled', 'review_received')",
            name="check_notification_type",
        ),
        Index("idx_notifications_user_read", "user_id", "read_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    read_at: Mapped[Optional[str]] = mapped_column(String(35), nullable=True)
    created_at: Mapped[str] = mapped_column(String(35), nullable=False, default=utc_now_iso)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="notifications")
