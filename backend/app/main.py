import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.core.limiter import limiter
from app.db import init_db
from app.errors import register_exception_handlers
from app.routers.auth import router as auth_router
from app.routers.bookings import router as bookings_router
from app.routers.catalog import router as catalog_router
from app.routers.health import router as health_router
from app.routers.host import router as host_router
from app.routers.meta import router as meta_router
from app.routers.notifications import router as notifications_router
from app.routers.users import router as users_router
from app.routers.wishlist import router as wishlist_router
from seed.seed import seed_database

settings = get_settings()

DEFAULT_JWT_SECRET = "supersecretjwtkeyforairbnbcloneproductionmustbe32charsorlonger!"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize tables and seed if database is empty (PRD §17 / §18)
    if not settings.DATABASE_URL.startswith("sqlite:///:memory:"):
        init_db()
        try:
            seed_database(reset=False)
        except Exception:
            # Avoid crashing if seed was already run concurrently
            pass
    yield


def create_app() -> FastAPI:
    # Production guard: refuse to boot with default or short JWT_SECRET (PRD §11)
    if settings.ENV == "production":
        if (
            len(settings.JWT_SECRET) < 32
            or settings.JWT_SECRET == DEFAULT_JWT_SECRET
            or "changeme" in settings.JWT_SECRET.lower()
        ):
            raise RuntimeError(
                "Production environment requires a secure, non-default JWT_SECRET of at least 32 characters."
            )

    app = FastAPI(
        title="Airbnb Clone API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Attach slowapi state
    app.state.limiter = limiter
    app.add_middleware(SlowAPIMiddleware)

    # Security & Request ID middleware
    @app.middleware("http")
    async def request_id_and_security_headers_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        # Content-type guard for mutations (PRD §7 / §8.5)
        # Mutations must be JSON (or multipart for uploads)
        if request.method in ("POST", "PUT", "PATCH") and not request.url.path.startswith("/api/uploads"):
            content_type = request.headers.get("content-type", "")
            content_length = request.headers.get("content-length", "0")
            has_body = content_length != "0" or "transfer-encoding" in request.headers
            if has_body and not content_type.startswith("application/json") and not request.url.path.endswith("/logout"):
                return JSONResponse(
                    status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                    content={
                        "error": {
                            "code": "UNSUPPORTED_MEDIA_TYPE",
                            "message": "Content-Type must be application/json",
                            "fields": {},
                        }
                    },
                )

        response: Response = await call_next(request)

        # Set headers
        response.headers["X-Request-ID"] = req_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # CORS for development
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_ORIGIN, "http://localhost:3000"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Static uploads mount
    upload_path = Path(settings.UPLOAD_DIR)
    upload_path.mkdir(parents=True, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

    # Exception handlers
    register_exception_handlers(app)

    # Include routers under /api
    app.include_router(health_router, prefix="/api")
    app.include_router(meta_router, prefix="/api")
    app.include_router(auth_router, prefix="/api")
    app.include_router(users_router, prefix="/api")
    app.include_router(catalog_router, prefix="/api")
    app.include_router(wishlist_router, prefix="/api")
    app.include_router(bookings_router, prefix="/api")
    app.include_router(host_router, prefix="/api")
    app.include_router(notifications_router, prefix="/api")

    return app


app = create_app()
