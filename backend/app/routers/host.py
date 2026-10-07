"""
Host router: listing CRUD, reservations, dashboard, file uploads.
"""
import uuid
from pathlib import Path
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, File, Query, UploadFile
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.deps import require_host
from app.errors import ConflictError
from app.models.user import User
from app.schemas.host import (
    CreateListingRequest,
    HostDashboardResponse,
    HostListingResponse,
    UpdateListingRequest,
    UploadResponse,
)
from app.services.host import (
    create_listing,
    delete_listing,
    get_host_dashboard,
    get_host_listing,
    get_host_listings,
    get_host_reservations,
    update_listing,
)
from app.core.dates import get_server_today as get_today

router = APIRouter(tags=["Host"])

DbDep = Annotated[Session, Depends(get_db)]
HostDep = Annotated[User, Depends(require_host)]
settings = get_settings()

# ─── Dashboard ────────────────────────────────────────────────────────────────

@router.get("/host/dashboard", response_model=HostDashboardResponse)
def host_dashboard(db: DbDep, host: HostDep):
    """High-level metrics for the host's dashboard."""
    today_str = get_today()
    result = get_host_dashboard(db, host.id, today_str)
    return HostDashboardResponse(**result)


# ─── Listings ──────────────────────────────────────────────────────────────────

@router.get("/host/listings", response_model=list[HostListingResponse])
def list_host_listings(db: DbDep, host: HostDep):
    """List all non-deleted listings owned by the current host."""
    today_str = get_today()
    results = get_host_listings(db, host.id, today_str)
    return [HostListingResponse(**r) for r in results]


@router.post("/host/listings", status_code=201)
def create_host_listing(body: CreateListingRequest, db: DbDep, host: HostDep):
    """Create a new listing."""
    today_str = get_today()
    listing = create_listing(db, host, body.model_dump())
    result = get_host_listing(db, listing.id, host.id, today_str)
    return HostListingResponse(**result)


@router.get("/host/listings/{listing_id}", response_model=HostListingResponse)
def get_host_listing_endpoint(listing_id: str, db: DbDep, host: HostDep):
    """Get a single host-owned listing."""
    today_str = get_today()
    result = get_host_listing(db, int(listing_id), host.id, today_str)
    return HostListingResponse(**result)


@router.put("/host/listings/{listing_id}", response_model=HostListingResponse)
def update_host_listing(listing_id: str, body: UpdateListingRequest, db: DbDep, host: HostDep):
    """Full or partial update to a host-owned listing."""
    today_str = get_today()
    update_listing(db, int(listing_id), host.id, body.model_dump(exclude_none=True))
    result = get_host_listing(db, int(listing_id), host.id, today_str)
    return HostListingResponse(**result)


@router.delete("/host/listings/{listing_id}", status_code=204)
def delete_host_listing(listing_id: str, db: DbDep, host: HostDep):
    """Soft-delete a listing (409 if upcoming bookings exist)."""
    today_str = get_today()
    delete_listing(db, int(listing_id), host.id, today_str)


# ─── Reservations ─────────────────────────────────────────────────────────────

@router.get("/host/reservations")
def host_reservations(
    db: DbDep,
    host: HostDep,
    tab: str = Query("all", pattern="^(all|upcoming|past)$"),
    listing_id: Optional[str] = Query(None),
):
    """List all reservations across host's listings, optionally filtered."""
    today_str = get_today()
    lid = int(listing_id) if listing_id else None
    return get_host_reservations(db, host.id, today_str, tab=tab, listing_id=lid)


# ─── File Upload ───────────────────────────────────────────────────────────────

ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG"
WEBP_MAGIC_RIFF = b"RIFF"
WEBP_MAGIC_WEBP = b"WEBP"
GIF_MAGIC = b"GIF8"


def _detect_mime(header: bytes) -> str | None:
    """Detect image MIME type from magic bytes."""
    if header[:3] == JPEG_MAGIC:
        return "image/jpeg"
    if header[:4] == PNG_MAGIC:
        return "image/png"
    if header[:4] == GIF_MAGIC:
        return "image/gif"
    if header[:4] == WEBP_MAGIC_RIFF and header[8:12] == WEBP_MAGIC_WEBP:
        return "image/webp"
    return None


@router.post("/uploads", response_model=UploadResponse, status_code=201)
async def upload_image(
    file: UploadFile = File(...),
    host: User = Depends(require_host),
):
    """
    Upload a listing photo. Validates via magic bytes (not just extension/MIME header).
    Max 5MB. Returns the URL path for use in listing creation.
    """
    # Read first 5MB + 1 byte to check size limit
    content = await file.read(MAX_UPLOAD_SIZE + 1)
    if len(content) > MAX_UPLOAD_SIZE:
        raise ConflictError(
            "File too large. Maximum upload size is 5MB.",
            code="FILE_TOO_LARGE",
        )

    # Magic-byte validation (PRD §8.3 / §10.9)
    detected_mime = _detect_mime(content[:12])
    if not detected_mime:
        raise ConflictError(
            "Unsupported file type. Only JPEG, PNG, WebP, and GIF are allowed.",
            code="INVALID_FILE_TYPE",
        )

    # Generate UUID filename with correct extension
    ext_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }
    ext = ext_map[detected_mime]
    filename = f"{uuid.uuid4().hex}{ext}"

    # Optionally re-encode with Pillow if available (degrades gracefully)
    try:
        from PIL import Image as PILImage
        import io as _io
        img = PILImage.open(_io.BytesIO(content))
        img.verify()  # raises if corrupt
        # Re-open after verify (PIL requirement)
        img = PILImage.open(_io.BytesIO(content))
        output = _io.BytesIO()
        save_format = {"image/jpeg": "JPEG", "image/png": "PNG", "image/webp": "WEBP", "image/gif": "GIF"}[detected_mime]
        img.save(output, format=save_format)
        content = output.getvalue()
    except ImportError:
        pass  # Pillow not available, store raw bytes
    except Exception:
        raise ConflictError("Corrupted or invalid image file.", code="INVALID_IMAGE")

    # Write to upload directory
    upload_path = Path(settings.UPLOAD_DIR) / filename
    upload_path.parent.mkdir(parents=True, exist_ok=True)
    upload_path.write_bytes(content)

    url = f"/uploads/{filename}"
    return UploadResponse(url=url, filename=filename)
