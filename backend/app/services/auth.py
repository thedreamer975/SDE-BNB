from sqlalchemy import select
from sqlalchemy.orm import Session
from app.errors import ConflictError, UnauthenticatedError
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest
from app.security import (
    create_access_token,
    hash_password,
    verify_password,
    verify_password_constant_time,
)


def register_user(db: Session, data: RegisterRequest) -> tuple[User, str]:
    """Register a new user account with role='guest' and generate JWT."""
    existing = db.scalar(select(User).where(User.email == data.email))
    if existing:
        raise ConflictError(
            message="An account with this email already exists.",
            fields={"email": "An account with this email already exists."},
        )

    pwd_hash = hash_password(data.password)
    user = User(
        name=data.name,
        email=data.email,
        password_hash=pwd_hash,
        role="guest",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return user, token


def authenticate_user(db: Session, data: LoginRequest) -> tuple[User, str]:
    """
    Authenticate user by email and password using constant-time verification.
    Returns authenticated user and JWT token.
    """
    user = db.scalar(select(User).where(User.email == data.email))
    if user is None:
        # Constant-time dummy verify prevents email enumeration attacks (PRD §7)
        verify_password_constant_time(data.password, None)
        raise UnauthenticatedError("Incorrect email or password.")

    if not verify_password(data.password, user.password_hash):
        raise UnauthenticatedError("Incorrect email or password.")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return user, token
