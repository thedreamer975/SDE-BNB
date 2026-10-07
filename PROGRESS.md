# Progress Log — Airbnb Clone

## S0: Scaffold & Tooling
- **Status:** PASS
- **Built:** Monorepo, FastAPI backend, Next.js 14 frontend, Tailwind tokens, Makefile, contracts, and type generator.
- **Commit:** `3edd2f2` pushed to remote.

## S1: Data Layer & Seed
- **Status:** In Progress
- **Plan:**
  - Define SQLAlchemy 2.0 ORM models with `Mapped[]` and full constraints (CHECK, UNIQUE, FK, INDEX) in `backend/app/models/`:
    `user.py`, `listing.py`, `amenity.py`, `booking.py`, `review.py`, `wishlist.py`, `notification.py`
  - Implement `backend/app/services/pricing.py` with the canonical quote calculation (`round_half_up(subtotal * 0.12)`, integer cents)
  - Implement confirmation code generator in `backend/app/core/codes.py`
  - Implement seed system in `backend/seed/`: amenities dataset, 12 destinations × 3 listings (36), hosts/guests, confirmed/cancelled bookings with same-day turnover, reviews with sub-scores and aggregates, wishlist items, notifications, and superhost calculation
  - Implement `backend/seed/verify_images.py` with image URL validation and fallback
  - Ensure auto-seed on app startup if database is empty, plus idempotent CLI reset flag `--reset`
  - Write test suite `backend/tests/test_models.py` and `backend/tests/test_seed.py`
  - Integration check: verify table schemas, constraints, SQLite foreign keys, query plan on overlap index
- **Files touched:**
  - `backend/app/models/__init__.py`
  - `backend/app/models/user.py`
  - `backend/app/models/amenity.py`
  - `backend/app/models/listing.py`
  - `backend/app/models/booking.py`
  - `backend/app/models/review.py`
  - `backend/app/models/wishlist.py`
  - `backend/app/models/notification.py`
  - `backend/app/services/__init__.py`
  - `backend/app/services/pricing.py`
  - `backend/app/core/codes.py`
  - `backend/seed/__init__.py`
  - `backend/seed/data.py`
  - `backend/seed/verify_images.py`
  - `backend/seed/seed.py`
  - `backend/app/main.py`
  - `backend/tests/test_models.py`
  - `backend/tests/test_seed.py`
  - `docs/CONTRACTS.md`
- **Decisions:**
  - D-S1-1: Use Crockford-style uppercase alphanumeric charset `(2-9, A-Z excluding I, O)` for 10-character booking confirmation codes to prevent character confusion.
  - D-S1-2: Auto-seed executes on startup if `users` table count is 0, ensuring zero-configuration boot on Railway/Render.
- **Risks:**
  - Seed execution performance; batch insert seed records within a single transaction to keep startup fast (<1 second).
