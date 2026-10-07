from app.schemas.catalog import ListingCardResponse

# Wishlist returns array of ListingCardResponse
WishlistListResponse = list[ListingCardResponse]
WishlistIdsResponse = list[int]
