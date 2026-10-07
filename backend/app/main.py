import uuid
from pathlib import Path
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from app.config import get_settings
from app.errors import register_exception_handlers
from app.routers.health import router as health_router

from contextlib import asynccontextmanager
from app.db import init_db
from seed.seed import seed_database

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Auto-initialize tables and seed if database is empty (PRD §17 / §18)
    if not settings.DATABASE_URL.startswith("sqlite:///:memory:"):
        init_db()
        try:
            seed_database(reset=False)
        except Exception as e:
            # Avoid crashing if seed was already run concurrently
            pass
    yield


def create_app() -> FastAPI:
    # Production guard: check JWT secret
    if settings.ENV == "production" and len(settings.JWT_SECRET) < 32:
        raise RuntimeError("Production environment requires a JWT_SECRET of at least 32 characters")

    app = FastAPI(
        title="Airbnb Clone API",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # Security & Request ID middleware
    @app.middleware("http")
    async def request_id_and_security_headers_middleware(request: Request, call_next):
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = req_id

        # Content-type guard for mutations (PRD §7 / §8.5)
        # Mutations must be JSON or multipart (for uploads)
        if request.method in ("POST", "PUT", "PATCH") and not request.url.path.startswith("/api/uploads"):
            content_type = request.headers.get("content-type", "")
            # Only validate if there is a body expected
            content_length = request.headers.get("content-length", "0")
            if content_length != "0" and not content_type.startswith("application/json") and not request.url.path.endswith("/logout"):
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

    return app


app = create_app()
