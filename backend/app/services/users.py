from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UpdateUserRequest
from app.security import create_access_token


def update_user_profile(db: Session, user: User, data: UpdateUserRequest) -> User:
    """Update profile attributes for current user."""
    user.name = data.name
    db.commit()
    db.refresh(user)
    return user


def become_host(db: Session, user: User) -> tuple[User, str]:
    """Promote user to host role (one-way) and reissue session token."""
    user.role = "host"
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id), "role": user.role})
    return user, token
