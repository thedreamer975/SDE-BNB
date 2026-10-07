from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.errors import NotFoundError
from app.models.listing import Listing
from app.models.wishlist import WishlistItem


def get_user_wishlist_ids(db: Session, user_id: int) -> list[int]:
    """Return list of listing IDs saved by the user."""
    stmt = (
        select(WishlistItem.listing_id)
        .join(Listing, WishlistItem.listing_id == Listing.id)
        .where(
            WishlistItem.user_id == user_id,
            Listing.deleted_at.is_(None),
        )
    )
    return list(db.scalars(stmt).all())


def get_user_wishlist(db: Session, user_id: int) -> list[Listing]:
    """
    Return full Listing models saved by user.
    Omits soft-deleted listings (PRD §10.6).
    Eager loads photos and amenities to prevent N+1 queries.
    """
    stmt = (
        select(Listing)
        .join(WishlistItem, WishlistItem.listing_id == Listing.id)
        .where(
            WishlistItem.user_id == user_id,
            Listing.deleted_at.is_(None),
        )
        .options(
            selectinload(Listing.photos),
            selectinload(Listing.amenities),
        )
        .order_by(WishlistItem.created_at.desc())
    )
    return list(db.scalars(stmt).all())


def add_to_wishlist(db: Session, user_id: int, listing_id: int) -> None:
    """Idempotently add a listing to user's wishlist."""
    listing = db.get(Listing, listing_id)
    if not listing or listing.deleted_at is not None:
        raise NotFoundError("Listing not found.")

    existing = db.scalar(
        select(WishlistItem).where(
            WishlistItem.user_id == user_id,
            WishlistItem.listing_id == listing_id,
        )
    )
    if existing:
        return

    item = WishlistItem(user_id=user_id, listing_id=listing_id)
    db.add(item)
    db.commit()


def remove_from_wishlist(db: Session, user_id: int, listing_id: int) -> None:
    """Idempotently remove a listing from user's wishlist."""
    item = db.scalar(
        select(WishlistItem).where(
            WishlistItem.user_id == user_id,
            WishlistItem.listing_id == listing_id,
        )
    )
    if item:
        db.delete(item)
        db.commit()
