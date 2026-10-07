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

