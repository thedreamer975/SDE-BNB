import jwt
from fastapi import Depends, Request
from sqlalchemy.orm import Session
from app.core.cookies import COOKIE_NAME
from app.db import get_db
from app.errors import ForbiddenError, UnauthenticatedError
from app.models.user import User
from app.security import decode_access_token


def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """
    Extract current user from session cookie (or Bearer token fallback).
    Always loads the fresh user record from the database to ensure
    role changes and deletions apply immediately (PRD §7).
    """
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        # Fallback to Authorization header if present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

    if not token:
        return None

    try:
        payload = decode_access_token(token)
        sub = payload.get("sub")
        if sub is None:
            return None
        user_id = int(sub)
    except (jwt.PyJWTError, ValueError, TypeError):
        return None

    user = db.get(User, user_id)
    return user


def get_current_user(
    user: User | None = Depends(get_current_user_optional),
) -> User:
    """Ensure user is authenticated, otherwise raise 401 UnauthenticatedError."""
    if user is None:
        raise UnauthenticatedError("Authentication required.")
    return user


def require_host(
    user: User = Depends(get_current_user),
) -> User:
    """Ensure current user has the host role, otherwise raise 403 ForbiddenError."""
    if user.role != "host":
        raise ForbiddenError("Host permissions required to perform this action.")
    return user
