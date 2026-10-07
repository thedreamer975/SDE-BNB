# API & Component Contracts

This document records the exact contracts (endpoints, payloads, shared types, exported components/hooks) established across segments.

## S0: Scaffold & Tooling

### Endpoints
| Method | Path | Auth | Request Shape | Response Shape |
|---|---|---|---|---|
| `GET` | `/api/health` | Public | None | `{"status": "ok"}` |

### Proxy & Rewrites
- Next.js proxies `/api/:path*` to `API_ORIGIN` (default `http://localhost:8000/api/:path*`)
- Next.js proxies `/uploads/:path*` to `API_ORIGIN` (default `http://localhost:8000/uploads/:path*`)

### Error Envelope Contract (PRD §8.2)
All non-2xx responses conform to:
```json
{
  "error": {
    "code": "STRING_CODE",
    "message": "Human readable message",
    "fields": {}
  }
}
```

### Generated Types
- Source: FastAPI OpenAPI schema (`/openapi.json`)
- Target: `frontend/lib/types.gen.ts` via `npm run gen:types`

## S2: Authentication & Authorization: Backend

### Endpoints
| Method | Path | Auth | Request Shape | Response Shape |
|---|---|---|---|---|
| `POST` | `/api/auth/register` | Public (5/min rate limit) | `{"name": string, "email": string, "password": string}` | `UserResponse` (sets `session` cookie, 201 Created) |
| `POST` | `/api/auth/login` | Public (5/min rate limit) | `{"email": string, "password": string}` | `UserResponse` (sets `session` cookie, 200 OK) |
| `POST` | `/api/auth/logout` | Public | None | `204 No Content` (clears `session` cookie) |
| `GET` | `/api/auth/me` | Authenticated | None | `UserResponse` (200 OK) |
| `PATCH` | `/api/users/me` | Authenticated | `{"name": string}` (2-60 chars) | `UserResponse` (200 OK) |
| `POST` | `/api/users/me/become-host` | Authenticated | None | `UserResponse` (reissues `session` cookie with host role, 200 OK) |

### Shared Schemas & Types
- **UserResponse**:
  ```json
  {
    "id": 1,
    "name": "Jane Doe",
    "email": "jane@example.com",
    "role": "guest",
    "avatar_url": null,
    "is_superhost": false,
    "created_at": "2026-10-07T12:00:00Z"
  }
  ```
  *Note: `password_hash` is strictly excluded from all response models.*

### Cookie Contract
- **Cookie Name:** `session`
- **Attributes:** `HttpOnly; Path=/; SameSite=Lax; Max-Age=604800` (7 days); `Secure` enforced in production.
- **Payload:** HS256 JWT with claims:
  - `sub`: stringified user id (`str(user.id)`)
  - `role`: string (`"guest"` or `"host"`)
  - `iat`: timestamp
  - `exp`: expiration timestamp (7 days)
  - `jti`: unique UUID v4 string

### Auth Dependencies Exported (`app.deps`)
- `get_current_user_optional(request: Request, db: Session) -> User | None`: Extracts user from cookie or returns None.
- `get_current_user(user: User = Depends(get_current_user_optional)) -> User`: Enforces authentication, raises `401 UNAUTHENTICATED`.
- `require_host(user: User = Depends(get_current_user)) -> User`: Enforces host role, raises `403 FORBIDDEN`.

## S3: Catalog API: Listings, Search, Availability, Wishlist

### Endpoints
| Method | Path | Auth | Request Shape / Params | Response Shape |
|---|---|---|---|---|
| `GET` | `/api/meta` | Public | None | `MetaResponse` (`{today, categories[], property_types[], room_types[], amenities[], limits}`) |
| `GET` | `/api/search/suggestions` | Public | `q` (string query) | `list[DestinationSuggestion]` (`[{label, city, country, lat, lng}]`) |
| `GET` | `/api/listings` | Optional | Query parameters (see mapping table below) | `ListingListResponse` (`{items[], total, page, page_size, has_more}`) |
| `GET` | `/api/listings/count` | Public | Same filter query parameters | `ListingCountResponse` (`{total}`) |
| `GET` | `/api/listings/facets` | Public | Same filter query parameters (excluding price) | `ListingFacetsResponse` (`{price_min, price_max, histogram[{from, to, count}]}`) |
| `GET` | `/api/listings/{id}` | Optional | `id` (int path) | `ListingDetailResponse` (includes photos, amenities, host, rating, `saved`) |
| `GET` | `/api/listings/{id}/availability` | Public | `from` (date), `to` (date) | `AvailabilityResponse` (`{booked:[{check_in, check_out}], min_nights, max_nights, max_advance_days}`) |
| `GET` | `/api/listings/{id}/reviews` | Public | `page` (int), `page_size` (int) | `ReviewsListResponse` (`{items[], summary{avg, count, categories}, total, has_more}`) |
| `GET` | `/api/wishlist` | Authenticated | None | `list[ListingCardResponse]` (`saved=true`) |
| `GET` | `/api/wishlist/ids` | Authenticated | None | `list[int]` (array of saved listing IDs) |
| `PUT` | `/api/wishlist/{id}` | Authenticated | `id` (int path) | `204 No Content` (idempotent add) |
| `DELETE` | `/api/wishlist/{id}` | Authenticated | `id` (int path) | `204 No Content` (idempotent remove) |

### Parameter Mapping Table (Frontend URL State ⇄ Backend API)
| Frontend URL Param (S5) | Backend Query Param | Format / Constraint | Example |
|---|---|---|---|
| `location` | `location` | Substring match on city, country, title | `Goa` |
| `checkIn` | `check_in` | `YYYY-MM-DD` string | `2026-11-05` |
| `checkOut` | `check_out` | `YYYY-MM-DD` string (must be > check_in) | `2026-11-10` |
| `adults` | `adults` | Integer >= 1 | `2` |
| `children` | `children` | Integer >= 0 | `1` |
| `infants` | `infants` | Integer >= 0 | `0` |
| `pets` | `pets` | Integer >= 0 (requires `pets_allowed=1`) | `1` |
| `category` | `category` | Exact category name | `Beachfront` |
| `roomTypes` | `room_types` | Multi-value query param | `entire_home` |
| `propertyTypes` | `property_types` | Multi-value query param | `Villa` |
| `minPrice` | `min_price_cents` | Dollars in URL -> cents in query | `$50` -> `5000` |
| `maxPrice` | `max_price_cents` | Dollars in URL -> cents in query | `$300` -> `30000` |
| `bedrooms` | `min_bedrooms` | Integer >= | `2` |
| `beds` | `min_beds` | Integer >= | `3` |
| `baths` | `min_baths` | Float >= | `1.5` |
| `amenities` | `amenity_ids` | Multi-value integer IDs (all-of match) | `1`, `3` |
| `superhost` | `superhost` | Boolean `true` or `false` | `true` |
| `page` | `page` | Integer (default 1) | `1` |
| `pageSize` | `page_size` | Integer (default 20, max 40) | `20` |

### Derived Listing Card Attributes
- `guest_favorite`: Derived boolean, True when `rating_avg >= 4.8 AND rating_count >= 5`.
- `saved`: Hydrated boolean, True when current authenticated user has listing in `wishlist_items`.
- `is_superhost`: Denormalized boolean from host user record.
- `photos`: First 5 photos sorted by position.


