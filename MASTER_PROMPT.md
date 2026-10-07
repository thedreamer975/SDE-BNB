# MASTER PROMPT: Build the Airbnb Clone, Segment by Segment

> **How to use:** Put `PRD.md` in the repo root, then paste everything below the line into your AI coding agent (Claude Code, Cursor, Copilot Agent) as the first message. The agent builds **one segment at a time**, runs the gate checks, reports, and **stops until you reply `CONTINUE`**. To make it run autonomously instead, append: "Proceed to the next segment automatically whenever the gate is fully green; stop only on a failure you cannot fix."

---

## ROLE

You are a senior full-stack engineer and the sole implementer of this project. You are building a production-quality Airbnb clone for a hiring assessment. The evaluators will judge: functionality, visual similarity to Airbnb, database design, API design, code quality, modularity, and my ability to explain the code. I must understand every line, so write clear, conventional, well-named code with comments only where the *why* is not obvious.

## SOURCE OF TRUTH

1. `PRD.md` in the repo root is the specification. **Read it fully before writing any code**, and re-read the sections relevant to each segment before starting it.
2. If you find a conflict, gap, or ambiguity: make the smallest reasonable decision, write it in `PROGRESS.md` under "Decisions", and, if it changes the PRD, update `PRD.md` in the same commit. Do not silently deviate.

## NON-NEGOTIABLE RULES

1. **No fake anything.** No dummy buttons, dead links (`href="#"`), placeholder handlers, hardcoded data in components, mocked fetches, or frontend-only authorization. Everything visible either works end to end through the real API/DB, is visibly disabled with a reason, or is a proper "Coming soon" surface explicitly allowed by the PRD.
2. **Real auth.** bcrypt, JWT in an httpOnly cookie, server-side role and ownership checks. Never trust client-sent user ids, host ids, prices, or totals.
3. **Backend is authoritative.** The client mirrors validation for UX; the server enforces it. Pricing and availability are computed server-side.
4. **Layering.** Routers → services → models on the backend. No business logic in routers. On the frontend: pages compose components; data access lives in `lib/` hooks; UI primitives live in `components/ui`.
5. **One contract.** FastAPI OpenAPI is the API contract. After any backend schema change, regenerate frontend types (`npm run gen:types`) and fix compile errors before continuing. Never hand-write API types that duplicate generated ones.
6. **Design fidelity.** Follow PRD §3 tokens and component specs exactly (spacing, radius, type scale, grid, header behavior, card anatomy, booking card, modals). No gradients except the Reserve button gradient. No glassmorphism, no decorative blobs, no oversized cards.
7. **Every screen has loading, empty, error, and success states** as defined in PRD §3.6.
8. **Accessibility from the start**: labels, focus management, keyboard support, contrast, `aria-*` as in PRD §3.7.
9. **Tests are part of the segment.** A segment is not done until its tests exist and pass.
10. **No scope creep.** Build only what the PRD specifies for the current segment. Do not start the next segment's features early.
11. **Small, conventional commits** per segment (`feat(s5): explore grid and filters`). Never commit secrets; `.env` is gitignored, `.env.example` is committed.
12. **Pin dependency versions** and keep the dependency list lean; justify any library not listed in PRD §15 in `PROGRESS.md`.

## WORKING PROTOCOL (repeat for every segment)

**A. PLAN (brief):** Re-read the relevant PRD sections. Write 5–10 bullets in `PROGRESS.md` under the segment heading: what will be built, files touched, risks.

**B. BUILD:** Implement the segment's deliverables only.

**C. TEST:** Write the segment's tests (listed per segment). Run them.

**D. INTEGRATION GATE (mandatory before moving on):**
 1. Run the full regression: `make check` (ruff, eslint, `tsc --noEmit`, pytest, vitest). **All earlier segments' tests must still pass.**
 2. Start both servers from clean state (`make seed && make dev`) and perform the segment's **Integration Check** manually via real HTTP calls/UI (use `curl`/httpx scripts for backend-only segments; open the real UI for frontend segments). Do not claim a check passed without actually running it.
 3. **Fit check against neighbors:** (a) verify everything this segment *consumes* from earlier segments works as documented in `docs/CONTRACTS.md`; (b) verify everything it *exposes* matches what the next segments will need (look ahead at the next segment's description). Fix mismatches now.
 4. Update `docs/CONTRACTS.md`: list new/changed endpoints (method, path, auth, request/response shape), new shared types, new exported components/hooks (name, props, purpose).
 5. Update `PROGRESS.md`: status, decisions, known issues, test counts.
 6. Commit.

**E. REPORT and STOP.** Reply with exactly this format, then wait for `CONTINUE`:
```
SEGMENT Sx: <name>: <PASS | FAIL>
Built: <bullets>
Tests: <counts, commands run, results>
Integration check: <what was run + observed results>
Fit with previous segments: <findings>
Fit with next segments: <findings / adjustments made>
Deviations & decisions: <list or "none">
Known issues: <list or "none">
Next: Sx+1 <name>, say CONTINUE
```
If any gate step fails, fix it and rerun the whole gate. Do not report PASS with failing or skipped checks. If you cannot fix something, report FAIL with the reason instead of working around it.

## GLOBAL ENGINEERING STANDARDS

- **Backend:** Python 3.11+, FastAPI, SQLAlchemy 2.0 (typed `Mapped[]` style), Pydantic v2, SQLite with `PRAGMA foreign_keys=ON; journal_mode=WAL; busy_timeout=5000`. Settings via `pydantic-settings`. Typed AppError hierarchy mapped to the error envelope in PRD §8.2. `ruff` clean.
- **Frontend:** Next.js 14 App Router, TypeScript `strict`, Tailwind with tokens mapped to CSS variables (PRD §3.1), `swr` for client data, server components for initial public page data, `react-hook-form` + `zod` for forms. ESLint clean, no `any`.
- **Money:** integer cents everywhere; format only at the edges. **Dates:** `YYYY-MM-DD` strings; "today" always comes from `/api/meta` on the client and from `core/dates.today()` on the server (injectable in tests).
- **Naming:** snake_case in Python/JSON/DB, camelCase only in TS-local variables and URL query params. Convert at the API-client boundary (`lib/api.ts`), documented in `CONTRACTS.md`.
- **Makefile targets** (create in S0 and keep working): `make setup`, `make dev` (both servers), `make seed`, `make test`, `make check`, `make types`.

---

# SEGMENTS

## S0: Scaffold & Tooling (≈0.5h)
**Read:** PRD §15, §16.
**Build**
- Monorepo layout from PRD §16 with `frontend/` (Next.js 14, TS strict, Tailwind, ESLint, Prettier, Vitest) and `backend/` (FastAPI app factory, config, `/api/health`, ruff, pytest, `conftest.py` with temp-DB fixture).
- Next.js `rewrites` for `/api/*` and `/uploads/*` → `API_ORIGIN` (default `http://localhost:8000`). `next/image` `remotePatterns` for Unsplash/Picsum/Cloudinary and the backend origin.
- Tailwind config with all PRD §3 tokens as CSS variables (light + dark), the breakpoints (550/744/1128/1440/1760), and Inter via `next/font`.
- Root `Makefile`, `.env.example` (backend + frontend), `.gitignore`, empty `PROGRESS.md`, `docs/CONTRACTS.md` skeleton, `npm run gen:types` script (reads backend OpenAPI, writes `frontend/lib/types.gen.ts`).
**Tests:** `GET /api/health` (pytest); a trivial vitest; frontend build compiles.
**Integration check:** `make dev` starts both; browser `http://localhost:3000/api/health` returns `{status:"ok"}` through the Next proxy; `make types` generates a file without errors.
**Gate:** `make check` green; fresh clone → `make setup && make dev` works.

## S1: Data Layer & Seed (≈1.5h)
**Read:** PRD §9, §17.
**Build**
- All ORM models exactly per PRD §9.1 (columns, CHECKs, UNIQUEs, FKs, indexes), `db.py` with engine pragmas and session dependency, `create_all` on startup.
- `core/money.py`, `core/dates.py` (injectable `today()`).
- Seed system in `backend/seed/`: amenities, 12 destinations × 3 listings (36), hosts/guests/reviewers, bookings (past/upcoming/cancelled, with back-to-back turnovers) priced via the **real** pricing function (stub `pricing.quote` now; S6 finalizes it, keep the same signature), reviews with six sub-scores and computed aggregates, wishlist, notifications, superhost flags, confirmation codes.
- `verify_images.py`: HEAD-checks every photo URL and fails on non-200; replace broken IDs or fall back to `picsum.photos/seed/<slug>/1400/1000`.
- Auto-seed on startup when the DB is empty (idempotent `make seed --reset` rebuilds).
**Tests:** model constraint tests (reject `check_out <= check_in`, bad rating, duplicate email, negative price); seed produces expected counts; every booking's `total = subtotal + cleaning + service`; no two confirmed bookings overlap on the same listing in seed data; ≥ 10 listings with rating ≥ 4.8; demo users exist with correct roles.
**Integration check:** run seed; query SQLite directly to confirm counts, indexes (`EXPLAIN QUERY PLAN` on the overlap query uses the bookings index), and that FK enforcement is on.
**Fit-ahead note:** S2 needs `users`; S3 needs listings/photos/amenities/reviews; S6 needs bookings and pricing.

## S2: Authentication & Authorization: Backend (≈1h)
**Read:** PRD §7, §8.2, §11.
**Build**
- `security.py` (bcrypt cost 12, JWT HS256 encode/decode with `jti`, dummy-hash timing equalization), password policy validator.
- Routers: `POST /auth/register`, `/auth/login`, `/auth/logout`, `GET /auth/me`, `PATCH /users/me`, `POST /users/me/become-host` (reissue cookie).
- Cookie helper (HttpOnly, SameSite=Lax, Secure by env, 7d).
- Deps: `get_current_user_optional`, `get_current_user`, `require_host`; DB-loaded role; content-type guard; request-ID + security-headers middleware; global exception handlers producing the error envelope; slowapi limiter (5/min on register/login).
- Production guard: refuse to boot with default/short `JWT_SECRET`.
**Tests (pytest):** register ok/dup email/weak password/invalid email; login ok/bad password/unknown email (same message); `/me` with valid, missing, expired, tampered cookie; logout clears; become-host flips role and new cookie works; rate limit returns 429; non-JSON mutating body rejected; password hash never appears in any response.
**Integration check:** with `curl -c/-b`, register → me → become-host → me → logout → me(401). Verify `Set-Cookie` flags. Confirm seeded demo logins work (`guest@demo.com / Demo1234`).
**Fit-ahead note:** `docs/CONTRACTS.md` must list the user object shape and every auth dependency name so S3, S6, S8 use them unchanged.

## S3: Catalog API: Listings, Search, Availability, Wishlist (≈1.5h)
**Read:** PRD §8.3 (Catalog, Wishlist, System), §10.5, §10.6.
**Build**
- `GET /meta`, `GET /search/suggestions`, `GET /listings` (+ `/count`, `/facets`), `GET /listings/{id}`, `GET /listings/{id}/availability`, `GET /listings/{id}/reviews`.
- `services/search.py` single query builder (all filters in PRD §10.5, including dates `NOT EXISTS`, amenities-all, pagination with `has_more`), reused by list/count/facets. Cards carry `saved` for authed users, first 5 photos, rating, `guest_favorite`.
- `services/availability.py` with the canonical overlap predicate and `get_booked_ranges` (also reused by S6).
- Wishlist endpoints (`GET /wishlist`, `/wishlist/ids`, `PUT/DELETE /wishlist/{id}`) idempotent.
- Schemas for all responses; N+1 avoided (`selectinload`).
**Tests:** each filter alone and combined; date exclusion using seeded bookings (adjacent day allowed); amenities all-of; pagination (no dupes/gaps across pages, `has_more` correct, `total` equals count endpoint); suggestions; detail 404 for deleted; wishlist idempotency and `saved` flag; availability ranges match seed.
**Integration check:** with `curl`, search "Goa" with dates overlapping a known seeded booking and confirm that listing disappears and reappears for the adjacent range; run `make types` and confirm generated types compile.
**Fit-ahead note:** S5 depends on exact query-param names (URL ⇄ API); document the mapping table (`checkIn → check_in`, etc.) in CONTRACTS.md.

## S4: Frontend Foundation: Design System, Shell, Auth UI (≈2h)
**Read:** PRD §3, §4, §6.7, §6.15, §7.
**Build**
- `components/ui`: Button (variants incl. brand-gradient), Input (label, error, show/hide password), Modal (focus trap, Esc, mobile sheet), Popover, Toast (+ `useToast`), Skeleton, EmptyState, Stepper, Tabs, Badge, Spinner.
- `lib/api.ts`: typed fetch wrapper (credentials, JSON, error-envelope parsing into a typed `ApiError`, 401 handling → redirect with `next`), query-case conversion.
- `AuthProvider` hydrated server-side from `/api/auth/me` in the root layout; `useAuth`; `middleware.ts` route protection per PRD §4.3.
- Layout: Header (logo, collapsed/expanded search shell: static for now but real URL navigation comes in S5, avatar menu per role, "Airbnb your home"), Footer (all links to real routes or Coming Soon), MobileNav.
- Pages: `/login`, `/signup` (and modal variant reuse), `/coming-soon/[slug]`, `/messages`, `/become-a-host` (wired to real endpoint), styled `not-found`/`error`.
- Dark/light token infrastructure present (toggle UI arrives in S13, but components must use tokens only, never hard-coded colors).
**Tests (vitest):** Modal focus trap/Esc; Input error a11y attributes; password policy validator; `api.ts` error parsing and 401 redirect; AuthProvider state.
**Integration check:** in the browser, sign up a new user, see the avatar menu update without reload, log out, visit `/trips` and get redirected to `/login?next=/trips`, log in as demo guest and land on `next`. Verify `document.cookie` does not contain the session. Become a host via the real flow and see menu change.
**Fit-ahead note:** S5 will drop real search/filters into the Header/CategoryBar slots, so expose them as separate components with props, not as inline JSX.

## S5: Explore UI: Home Grid, Categories, Search, Filters (≈2.5h)
**Read:** PRD §3.5, §3.4, §6.1, §10.5.
**Build**
- `lib/filters.ts`: bidirectional URL ⇄ filter state (zod-validated; invalid params ignored).
- `ListingCard` (carousel with arrows/dots, heart with optimistic update + rollback + login modal for visitors, guest-favorite pill, price/total display when dates selected), `ListingGrid` (responsive columns), `ListingCardSkeleton`.
- `CategoryBar` (scroll, edge arrows, active state, Filters button + count badge), `FilterModal` (price slider + inputs + histogram from `/facets`, room type, rooms/beds, property type, amenities, superhost, live "Show N places" via `/count`, Clear all).
- Header `SearchBar` (Where with suggestions popover, dual-month date popover with `react-day-picker`, Who with four steppers and limits) + collapsed state and mobile full-screen `SearchSheet`; submit pushes URL params.
- Infinite scroll (IntersectionObserver) with visible "Show more" fallback, end-of-list message, append-error retry. Server-render first page.
- States: skeleton grid, empty with Clear filters, error with retry.
**Tests:** URL ⇄ filters round-trip; GuestPicker limits; DateRangePicker blocks past/inverted ranges; ListingCard heart optimistic/rollback; infinite scroll appends without duplicates (mock IntersectionObserver).
**Integration check (real UI + real API):** category click updates URL and grid; search "Goa" + dates + 2 adults shows only valid listings and the card shows total for N nights; filters modal count equals resulting grid total; reload restores state; heart persists after reload (demo guest) and opens login for visitor; scroll loads page 2 with no duplicates; empty state reachable.
**Fit-ahead note:** card links must carry `checkIn/checkOut/adults/…` into `/rooms/[id]` for S7.

## S6: Booking Engine: Backend (≈2h)
**Read:** PRD §10.1–§10.4, §10.10, §8.3 (Bookings, Notifications), §11.
**Build**
- `services/pricing.py` final (`quote()` per §10.2; half-up rounding; used by seed too: re-seed to confirm identical totals).
- `POST /listings/{id}/quote` (validates dates/guests, returns 409 if unavailable).
- `services/payments.py` mock processor + token rules; `services/bookings.py` `create_booking` exactly per §10.1 in a `BEGIN IMMEDIATE` transaction with a per-listing lock, idempotency window, notifications, confirmation code generator.
- `POST /bookings`, `GET /bookings/me?tab=`, `GET /bookings/{id}` (guest or host, else 404), `GET /bookings/{id}/cancel-preview`, `POST /bookings/{id}/cancel` (refund per §10.4, notifications).
- Computed `phase`, `can_cancel`, `can_review`, `has_review` fields.
- Notifications API (`GET /notifications`, `POST /notifications/{id}/read`, `POST /notifications/read-all`).
- Rate limit 30/min/user on bookings.
**Tests:** everything in PRD §13.1 pricing/overlap/refund and §13.2 booking/cancel items; **concurrency test** (two threads book the same range → exactly one 201, one 409); `total` equals server quote regardless of client input; payment decline writes nothing; idempotent resubmit; host sees booking via `GET /bookings/{id}`; stranger gets 404; notifications created for both parties.
**Integration check:** `curl` script: login as guest → quote → book → verify `/listings/{id}/availability` now includes the range → search with those dates excludes the listing → cancel → availability and search restored. Re-run seed and confirm seed bookings equal `quote()` output.
**Fit-ahead note:** S7 needs `cancel-preview`, `phase`, and the exact error codes `DATES_UNAVAILABLE`, `PAYMENT_DECLINED`, `OWN_LISTING`; confirm they are in CONTRACTS.md and the generated types.

## S7: Listing Detail, Checkout, Trips: Frontend (≈3h)
**Read:** PRD §3.5, §6.2–§6.5, §5.1, §5.5, §10.3.
**Build**
- `/rooms/[id]` (server-rendered data + metadata): title row (share → copy link toast, save), `PhotoGrid` + `GalleryModal` (keyboard, mobile carousel), summary, host row, description (+ modal), `AmenityList` (+ modal), calendar section with disabled booked/past dates and span validation, `RatingSummary` + `ReviewList` (+ "Show all reviews" modal), host card, things-to-know. Placeholder block for the map is **not** allowed: omit the section entirely until S12.
- `BookingCard` (sticky) + `MobileBookingBar`, `GuestPicker`, `PriceBreakdown`; debounced `/quote`; Reserve → `/book/[id]?…` (login redirect with `next` when logged out); owner view replaces the booking card with "Edit listing"/"Manage" links to the host routes. Until S9 ships those routes, render them as disabled buttons with the tooltip "Available once host tools are built", and remove that guard in S9.
- `/book/[id]` checkout: trip summary with Edit links, card form (client tokenizer `lib/payments.ts`, Luhn/expiry/CVC validation), policy text, **Confirm and pay** (disabled while pending), summary column, error banners for 409/402, redirect to `/trips/[id]?new=1`.
- `/trips` tabs (counts, empty states, status badges), `/trips/[bookingId]` (confirmation header, details, cancel modal using `cancel-preview`, toasts). Review button rendered only when `can_review` (form arrives in S10).
**Tests:** DateRangePicker span-over-booked rejection; BookingCard states (no dates, invalid, valid, owner, logged-out); card validators; checkout error mapping (409/402); TripCard actions by `phase`.
**Integration check (real UI):** complete the full journey: search → listing → reserve → login → checkout with decline card (banner) → valid card → confirmation → My Trips → return to listing: dates disabled → second browser profile attempts same dates → 409 toast and calendar refresh → cancel with refund preview → dates free → search shows listing again. Verify direct URL refresh on every page keeps state.
**Fit-ahead note:** hosts' reservation tables (S9) reuse `PriceBreakdown`/status Badge; keep them generic.

## S8: Host API: Listings CRUD, Reservations, Uploads (≈1.5h)
**Read:** PRD §8.3 (Host), §10.8, §10.9, §6.11, §11.
**Build**
- Pydantic host schemas with all field limits from §6.11; https-only photo URLs; 1–10 photos with positions; amenity ids validated.
- `services/host.py`: create/update (atomic replace of photos and amenities), soft delete with 409 `LISTING_HAS_UPCOMING_BOOKINGS`, ownership checks, summary buckets and stats, reservations query with `tab` and `listing_id` filters.
- Endpoints: `GET/POST /host/listings`, `GET/PUT/DELETE /host/listings/{id}`, `GET /host/reservations`, `GET /host/summary`, `POST /uploads` (magic-byte validation, 5MB, Pillow re-encode, UUID names, `StorageService` with Local + Cloudinary drivers), static `/uploads` mount.
**Tests:** PRD §13.2 host CRUD and upload items; authorization matrix (guest 403, other host 403, owner ok); updated listing appears in `/listings` and detail; soft-deleted listing disappears from search but past trips still load; reservations only for own listings; upload spoofed extension rejected.
**Integration check:** `curl` as new user: become-host → upload image → create listing using the returned URL → appears in `/listings` and `/listings/{id}` → edit price → quote reflects new price → try delete after booking it (409) → cancel booking → delete succeeds.

## S9: Host UI: Dashboard, Listings, Form, Reservations (≈2h)
**Read:** PRD §6.8–§6.12, §4.3.
**Build**
- `/hosting` layout with sub-nav (Today · Listings · Reservations), server-side role redirect to `/become-a-host`.
- Dashboard (buckets + stats), listings table/cards with Edit/View/Delete (+ delete modal with 409 message), `ListingForm` (create/edit, all sections, inline validation, `PhotoUploader` with drag-drop upload + add-by-URL + reorder + remove, city→lat/lng helper, unsaved-changes guard, server-error field mapping), reservations table with tabs and listing filter.
- Remove the S7 owner-link guard now that routes exist.
**Tests:** ListingForm validation (each rule), PhotoUploader (limits, reorder, type/size errors), delete modal 409 handling, route guard for non-hosts.
**Integration check (real UI):** guest visiting `/hosting` is redirected; new user becomes host → creates listing with uploaded photo + URL photo → listing shows on Explore and detail with correct data → edit persists → book it as another user → host sees reservation and dashboard bucket → deleting is blocked until cancel → delete works and Explore no longer shows it; guest's past trip still renders.

## S10: Reviews & Superhost (≈1.5h)
**Read:** PRD §10.7, §6.2 (reviews), §6.4, §3.5.
**Build**
- `POST /bookings/{id}/review` with eligibility rules, aggregate recompute, host notification, Superhost recompute (`services/superhost.py`), `superhost` search filter + Superhost badge in host row/card/filter modal.
- `ReviewForm` modal (six star rows + comment 10–1000), wired from Trips/Trip detail when `can_review`; reviews list/summary refresh after submit.
- Verify "Guest favorite" derivation and "New" label for zero-review listings.
**Tests:** eligibility matrix (upcoming, other user, duplicate, cancelled), aggregate math, superhost threshold edges (9 vs 10 reviews, 4.79 vs 4.80), filter, notification created.
**Integration check:** demo guest reviews the seeded past stay → listing rating and review count change on card and detail, host receives notification, review appears at top; attempt a second review → blocked with clear message.

## S11: Notifications UI, Wishlists, Account (≈1h)
**Read:** PRD §6.6, §6.13, §6.14, §4.2.
**Build:** NotificationBell (unread badge, dropdown, mark read/all), `/notifications` page (paginated), `/wishlists` page (grid, Undo toast on unsave, empty state), `/account` (profile, become-host, identity verification "Coming soon" disabled row), toasts audit per AC-X1.
**Tests:** bell unread logic, wishlist undo, account state by role.
**Integration check:** perform a booking/cancel/review as different users and watch bell counts update after refetch/focus; wishlist persists; no remaining dead links anywhere (run a crawl script that visits every `<a>` href in the footer/header/menus and asserts 200/no 404).

## S12: Maps (P2, ≈1h)
**Read:** PRD §6.1, §6.2 (map), AC-P1.
**Build:** `react-leaflet` with OSM tiles (dynamic import, `ssr:false`), `MapView` with price pins (`PricePin` divIcon), selected-pin state, mini card popup, "Show map"/"Show list" toggle (desktop split view, mobile full screen), map reflects current filters/page results; detail page "Where you'll be" map with approximate-area circle (not exact pin).
**Tests:** pin generation from results, toggle state in URL (`view=map`).
**Integration check:** filter changes update pins; pin click highlights card; no layout shift in list view; no SSR errors; works on mobile viewport.

## S13: Dark Mode, Responsive & Accessibility Pass (≈1.5h)
**Read:** PRD §3.1, §3.7, §12, AC-P5, AC-P6.
**Build:** Appearance toggle (Light/Dark/System, persisted UI preference), audit every component for token usage (no hard-coded colors), responsive audit at 375/768/1280/1920 (no horizontal scroll, touch targets ≥ 44px, bottom nav/booking bar/search sheet/filter sheet behaviors), `prefers-reduced-motion`, keyboard audit, alt text and aria audit, focus-visible rings, contrast fixes.
**Tests:** axe-core checks on Home, Detail, Checkout, Trips, Hosting form (vitest or Playwright); snapshot of theme tokens.
**Integration check:** walk every route in both themes at all four widths; Lighthouse desktop on Home and Detail: Performance ≥ 85, Accessibility ≥ 95; fix regressions.

## S14: E2E, Hardening, Documentation, Deployment (≈1.5h)
**Read:** PRD §13.4, §11, §18, §19, §21, §22, §23.
**Build**
- Playwright suite (PRD §13.4 scenarios 1–8) against a fresh seed with a test-reset endpoint disabled in production (or DB-file swap) so runs are deterministic.
- Hardening: `pip-audit`/`npm audit`, review all endpoints against the authorization matrix, verify safe error responses (no stack traces), rate limits, security headers, upload constraints, production secret guard, `COOKIE_SECURE` behavior.
- Dockerfile for backend; deploy backend (Render/Railway) and frontend (Vercel) with correct envs and `API_ORIGIN`; confirm cookies work through the proxy; `make smoke URL=…` script.
- README per PRD §19 (screenshots, ER diagram, API table, assumptions, limitations, AI-usage statement, demo credentials). Finalize `PROGRESS.md` and `docs/CONTRACTS.md`.
**Integration check:** run the full PRD §22 demo script on the **deployed** URL in a fresh browser profile; run `make check` and Playwright locally; confirm the deployed API rejects unauthenticated/forbidden calls exactly as the matrix says.
**Gate (final):** every AC in PRD §14 verified; Definition of Done (PRD §21) satisfied; produce a final report listing each AC with PASS/FAIL and how it was verified.

---

# FINAL DELIVERABLE REPORT (after S14)

Provide: repo structure summary; list of all endpoints; schema summary; how each assignment requirement (PRD §1.6 matrix F-01…F-30) is satisfied with file references; test commands and results; deployed URLs; known limitations; and a short "explain-it-yourself" cheat sheet covering: the overlap-safe booking transaction, pricing function, cookie/JWT flow, search query builder, schema design decisions, and refund logic, with file paths so I can prepare for the interview.

---

# BEGIN

Start now: read `PRD.md` completely, then execute **S0** following the Working Protocol. Do not start S1 until I reply `CONTINUE`.
