# Progress Log — Airbnb Clone

## S0: Scaffold & Tooling
- **Status:** PASS
- **Built:** Monorepo, FastAPI backend, Next.js 14 frontend, Tailwind tokens, Makefile, contracts, and type generator.
- **Commit:** `3edd2f2` pushed to remote.

## S1: Data Layer & Seed
- **Status:** PASS
- **Built:**
  - ORM models in `backend/app/models/` (`User`, `Listing`, `ListingPhoto`, `Amenity`, `Booking`, `Review`, `WishlistItem`, `Notification`)
  - Canonical pricing service `backend/app/services/pricing.py`
  - Deterministic seed system `backend/seed/` (30 amenities, 20 users, 36 listings with 5 photos each, 180+ bookings with same-day turnover, 160+ reviews, ratings aggregates, superhost calculation)
  - Image verification utility `verify_images.py`
  - Model constraint tests in `backend/tests/test_models.py` and seed verification in `backend/tests/test_seed.py`
- **Commit:** `a9d92fd` pushed to remote.

## S2: Authentication & Authorization: Backend
- **Status:** PASS
- **Built:**
  - `backend/app/security.py`: bcrypt (cost 12), JWT HS256 encode/decode with UUID `jti`, constant-time dummy verification for unknown emails, and password policy validator (>= 8 chars, <= 128 chars, >= 1 letter, >= 1 digit)
  - `backend/app/core/cookies.py`: httpOnly cookie helper setting and clearing `session` cookie (SameSite=Lax, Secure per env/flag, Path=/, Max-Age=604800)
  - `backend/app/core/limiter.py`: slowapi rate limiter configuration
  - `backend/app/schemas/`: `RegisterRequest`, `LoginRequest`, `UpdateUserRequest`, `UserResponse` with sanitize/validation rules
  - `backend/app/services/`: `auth.py` and `users.py` implementing isolated business logic
  - `backend/app/deps.py`: `get_current_user_optional`, `get_current_user`, `require_host` loading user freshly from DB on each request
  - `backend/app/routers/`: `auth.py` (`POST /register`, `POST /login`, `POST /logout`, `GET /me`) and `users.py` (`PATCH /me`, `POST /become-host`)
  - `backend/app/main.py`: mounted auth/users routers under `/api`, wired slowapi middleware and limiter, content-type mutation guard, security headers, production boot guard
  - `backend/app/errors.py`: mapped `RateLimitExceeded` to `RATE_LIMITED` (429) standard error envelope
  - `backend/tests/test_auth.py`: 17 comprehensive test cases
  - Generated TypeScript types synced to `frontend/lib/types.gen.ts`
- **Tests:**
  - Pytest: 29 passed (17 new auth tests + 12 previous regression tests)
  - Vitest: 2 passed
  - Lint: Ruff clean (0 errors), ESLint clean (0 errors), `tsc --noEmit` clean
- **Integration Check:**
  - Automated manual-flow script executed: register → /me → become-host → /me (role=host) → logout → /me (401 UNAUTHENTICATED).
  - Confirmed `Set-Cookie` contains `session=...; HttpOnly; Max-Age=604800; Path=/; SameSite=lax`.
  - Confirmed seeded demo accounts login with correct roles: `guest@demo.com` (guest) and `host@demo.com` (host).
- **Fit with previous segments:**
  - Consumed S1 `User` ORM model and SQLite session flawlessly.
- **Fit with next segments:**
  - S3 Catalog and Wishlist require `get_current_user_optional` and `get_current_user`; both are exported in `app.deps` and documented in `docs/CONTRACTS.md`.
  - S4 Frontend Auth requires endpoints `/api/auth/register`, `/api/auth/login`, `/api/auth/logout`, `/api/auth/me`, `/api/users/me`, `/api/users/me/become-host`; all exist and TypeScript definitions are generated in `frontend/lib/types.gen.ts`.
- **Decisions:**
  - D-S2-1: `POST /api/auth/logout` returns 204 No Content and clears the `session` cookie.
  - D-S2-2: `POST /api/auth/register` and `POST /api/auth/login` return 201/200 respectively with the authenticated user object in addition to setting the `session` cookie.
  - D-S2-3: Duplicate email during registration raises 409 Conflict with field error on `email` per PRD §6.7 & §8.2.
  - D-S2-4: Regex email validation applied in Pydantic schema avoiding additional unpinned dependencies.
- **Known issues:** None.
