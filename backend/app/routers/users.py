from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session
from app.core.cookies import set_auth_cookie
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.user import UpdateUserRequest, UserResponse
from app.services.users import become_host, update_user_profile

router = APIRouter(prefix="/users", tags=["Users"])


@router.patch("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def update_profile(
    payload: UpdateUserRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update profile name for currently authenticated user."""
    updated = update_user_profile(db, user, payload)
    return updated


@router.post("/me/become-host", status_code=status.HTTP_200_OK, response_model=UserResponse)
def handle_become_host(
    response: Response,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Promote user to host role and reissue refreshed session cookie."""
    updated, new_token = become_host(db, user)
    set_auth_cookie(response, new_token)
    return updated
