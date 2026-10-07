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
