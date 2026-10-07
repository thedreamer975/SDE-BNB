# Progress Log â€” Airbnb Clone

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
  - Automated manual-flow script executed: register â†’ /me â†’ become-host â†’ /me (role=host) â†’ logout â†’ /me (401 UNAUTHENTICATED).
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
  - D-S2-3: Duplicate email during registration raises 409 Conflict with field error on `email` per PRD Â§6.7 & Â§8.2.
  - D-S2-4: Regex email validation applied in Pydantic schema avoiding additional unpinned dependencies.
- **Known issues:** None.

## S3: Catalog API: Listings, Search, Availability, Wishlist
- **Status:** PASS
- **Built:**
  - `backend/app/services/availability.py`: date overlap predicate and `get_booked_ranges` query
  - `backend/app/services/search.py`: unified SQL query builder supporting all filters (location substring, guests capacity, pets, NOT EXISTS confirmed date overlap, categories, room types, property types, price range, rooms/beds/baths, all-of amenities match, superhost join, soft delete exclusion), 20-bucket price histogram, pagination, and derived `guest_favorite` badge
  - `backend/app/services/wishlist.py`: idempotent add/remove and listing card queries
  - `backend/app/schemas/`: `meta.py`, `catalog.py`, `wishlist.py`
  - `backend/app/routers/`: `meta.py` (`GET /api/meta`), `catalog.py` (`GET /api/search/suggestions`, `GET /api/listings`, `GET /api/listings/count`, `GET /api/listings/facets`, `GET /api/listings/{id}`, `GET /api/listings/{id}/availability`, `GET /api/listings/{id}/reviews`), `wishlist.py` (`GET /api/wishlist`, `GET /api/wishlist/ids`, `PUT/DELETE /api/wishlist/{id}`)
  - `backend/app/main.py`: mounted all catalog, meta, and wishlist routers under `/api`
  - Synced OpenAPI schema to `docs/openapi.json` and regenerated TypeScript definitions in `frontend/lib/types.gen.ts`
- **Tests:**
  - Pytest: 46 passed in `backend/tests/` (14 in `test_catalog.py`, 3 in `test_wishlist.py`, 17 in `test_auth.py`, 12 previous regression tests)
  - Vitest: 2 passed in `frontend/`
  - Full regression check (`python run.py check`): Ruff clean, ESLint clean, `npx tsc --noEmit` clean, Pytest 46 passed, Vitest 2 passed
- **Integration Check:**
  - Ran manual verification script querying seeded Goa listings:
    - Search without dates returned 3 Goa listings.
    - Search with dates overlapping confirmed seeded booking (2026-07-08 to 2026-07-13) excluded the booked listing.
    - Search with adjacent dates (2026-07-13 to 2026-07-16) confirmed the listing reappeared immediately (same-day turnover supported).
    - Verified `/api/meta` returns 14 categories, 30 amenities, system limits, and server today.
    - Verified `/api/search/suggestions` matches "Goa, India".
    - Verified `/api/listings/facets` generated 20 histogram buckets.
- **Fit with previous segments:**
  - Consumed S1 `Listing`, `ListingPhoto`, `Amenity`, `Booking`, `Review`, `WishlistItem` models and S2 `get_current_user_optional` and `get_current_user` auth dependencies.
- **Fit with next segments:**
  - Documented URL â‡„ API parameter mapping table in `docs/CONTRACTS.md` for S5 (Explore UI).
  - Exported all catalog endpoints and regenerated types in `frontend/lib/types.gen.ts`.
- **Decisions:**
  - D-S3-1: Search suggestion returns top 6 matching destinations plus static "Anywhere" and "Nearby" entry points per PRD Â§8.3.
  - D-S3-2: Date filtering requires both `check_in` and `check_out` or neither; providing only one returns 422 with validation error per PRD Â§10.5.
- **Known issues:** None.

## S4: Frontend Foundation — Shell, Design System, Auth UI
- **Status:** PASS
- **Built:**
  - `frontend/lib/api.ts`: Full typed API client for all backend endpoints with `ApiError` class (status, code, field_errors, request_id)
  - `frontend/lib/format.ts`: Centralized money (cents?USD), date, rating formatters per PRD D2
  - `frontend/lib/auth-context.tsx`: React context with `AuthProvider` providing `user`, `loading`, `refresh`, `setUser`, `logout`
  - `frontend/lib/toast-context.tsx`: Global dark snackbar system with 4s auto-dismiss, error/success/default types, action links
  - `frontend/middleware.ts`: Route protection (protected paths ? `/login?next=…`; auth-only paths redirect logged-in users to `/`)
  - `frontend/components/ui/Button.tsx`: All PRD variants (primary, brand/gradient, secondary, tertiary, ghost)
  - `frontend/components/ui/Input.tsx`: Accessible labeled input with error state, show/hide password toggle
  - `frontend/components/layout/Header.tsx`: Sticky header with custom Logo SVG, collapsed/expanded search pill, avatar menu (role-aware)
  - `frontend/components/layout/Footer.tsx`: 3-column link layout + copyright bar
  - `frontend/app/layout.tsx`: Root layout with `AuthProvider` + `ToastProvider`, Inter font
  - `frontend/app/(auth)/login/page.tsx`: Login form, server error mapping (401?generic, 429?rate limit), `?next` redirect
  - `frontend/app/(auth)/signup/page.tsx`: Signup with password strength hints, 409 duplicate email ? inline error per PRD D-S2-3
  - `frontend/app/become-a-host/page.tsx`: 3-step explainer ? `POST /become-host`
  - `frontend/app/coming-soon/[slug]/page.tsx`, `app/not-found.tsx`, `app/page.tsx` (shell)
- **Tests:** Pytest 46 passed, Vitest 2 passed, Ruff/ESLint/tsc all clean
- **Commit:** `7745f2d` pushed to remote.

## S5: Search/Explore UI (Listings Grid & Filters)
- **Status:** PASS
- **Built:**
  - `components/explore/CategoryBar.tsx`: Horizontally scrollable category list, active state styling, "Filters" trigger button.
  - `components/explore/ListingCard.tsx`: Grid item with heart wishlist toggle, guest-favorite badge, and `PhotoCarousel`.
  - `components/explore/ListingCardSkeleton.tsx`: Flat surface placeholder for loading states.
  - `components/ui/Modal.tsx`: Reusable accessible modal dialog using `<dialog>`.
  - `components/explore/FilterModal.tsx`: Comprehensive filter form with debounced `/listings/count` check.
  - `components/explore/ListingGrid.tsx`: Infinite scrolling grid mapped to `swr/infinite`.
  - `components/explore/ExploreContainer.tsx`: Client orchestrator bridging URL searchParams.
  - `app/page.tsx`: Replaced stub with `<ExploreContainer />` inside a `<Suspense>` boundary.
- **Tests:** Pytest 46 passed, Vitest 2 passed, ESLint and TSC clean.
- **Fit with next segments:** S6 (Bookings / Rooms) will take over when a user clicks on a `ListingCard`.
- **Known issues:** None.

## S6: Bookings & Rooms UI (Listing Details & Booking Widget)
- **Status:** PASS
- **Built:**
  - `app/rooms/[id]/page.tsx`: Server component scaffold handling basic layout and dynamic metadata generation for SEO.
  - `app/rooms/[id]/RoomDetailClient.tsx`: Main orchestrator displaying host information, description, amenities (with modal). Incorporates wishlist functionality via SWR.
  - `components/room/PhotoGrid.tsx`: Hero photo grid mimicking Airbnb's layout with "Show all photos" responsive modal.
  - `components/room/BookingWidget.tsx`: Sticky right-side panel with dynamic pricing calculation via `listings.quote()`, integrating natively typed inputs for check-in/out and guests. Navigates to /book/[id] on Reserve.
  - `components/room/ReviewSection.tsx`: Displays average rating, category scores, and top 6 reviews, with a modal for paginated full review history using `swr`.
- **Tests:** Pytest 46 passed, Vitest 2 passed, ESLint and TSC clean.
- **Fit with next segments:**
  - S7 (Host Dashboard) is the next functional segment for creating/managing listings.
- **Known issues:** Native date inputs used as an acceptable fallback instead of a full external calendar dependency, relying on backend 409/422 validation for booked dates.
