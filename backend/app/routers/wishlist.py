from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.catalog import ListingCardResponse
from app.services.search import listing_to_card
from app.services.wishlist import (
    add_to_wishlist,
    get_user_wishlist,
    get_user_wishlist_ids,
    remove_from_wishlist,
)

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])


@router.get("", response_model=list[ListingCardResponse])
def get_wishlist(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all saved listing cards for authenticated user."""
    listings = get_user_wishlist(db, user.id)
    return [listing_to_card(listing, saved=True) for listing in listings]


@router.get("/ids", response_model=list[int])
def get_wishlist_ids(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve saved listing IDs array for fast heart hydration."""
    return get_user_wishlist_ids(db, user.id)


@router.put("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def save_wishlist_item(
    listing_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Idempotently save a listing to user's wishlist."""
    add_to_wishlist(db, user.id, listing_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{listing_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wishlist_item(
    listing_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Idempotently remove a listing from user's wishlist."""
    remove_from_wishlist(db, user.id, listing_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
