from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.dates import get_server_today
from app.db import get_db
from app.models.amenity import Amenity
from app.schemas.meta import AmenityItem, MetaLimits, MetaResponse
from seed.data import CATEGORIES, PROPERTY_TYPES, ROOM_TYPES

router = APIRouter(tags=["System"])


@router.get("/meta", response_model=MetaResponse)
def get_system_metadata(db: Session = Depends(get_db)):
    """
    Return application metadata, system limits, and taxonomy per PRD §8.3.
    Client never calculates its own 'today' for business rules.
    """
    amenities = db.scalars(select(Amenity).order_by(Amenity.id.asc())).all()
    amenity_items = [
        AmenityItem(id=a.id, name=a.name, icon_key=a.icon_key, group=a.group)
        for a in amenities
    ]

    return MetaResponse(
        today=get_server_today(),
        categories=CATEGORIES,
        property_types=PROPERTY_TYPES,
        room_types=ROOM_TYPES,
        amenities=amenity_items,
        limits=MetaLimits(),
    )
