from fastapi import APIRouter, Depends, Request, Response, status
from sqlalchemy.orm import Session
from app.core.cookies import clear_auth_cookie, set_auth_cookie
from app.core.limiter import limiter
from app.db import get_db
from app.deps import get_current_user
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.schemas.user import UserResponse
from app.services.auth import authenticate_user, register_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
@limiter.limit("5/minute")
def register(
    request: Request,
    response: Response,
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    """Register new account, set session cookie, and return user representation."""
    user, token = register_user(db, payload)
    set_auth_cookie(response, token)
    return user


@router.post("/login", status_code=status.HTTP_200_OK, response_model=UserResponse)
@limiter.limit("5/minute")
def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate credentials, set session cookie, and return user representation."""
    user, token = authenticate_user(db, payload)
    set_auth_cookie(response, token)
    return user


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response):
    """Clear session cookie and invalidate local auth state."""
    clear_auth_cookie(response)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", status_code=status.HTTP_200_OK, response_model=UserResponse)
def get_me(user: User = Depends(get_current_user)):
    """Return currently authenticated user profile."""
    return user
