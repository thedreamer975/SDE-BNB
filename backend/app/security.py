import time
import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from app.config import get_settings

settings = get_settings()

# Constant dummy hash for timing equalization per PRD §7
DUMMY_HASH = bcrypt.hashpw(b"timing_equalization_dummy", bcrypt.gensalt(rounds=12)).decode("utf-8")


def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost 12."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against bcrypt hash."""
    try:
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


def verify_password_constant_time(plain_password: str, hashed_password: str | None) -> bool:
    """Constant-time password verification using dummy hash if user not found."""
    if hashed_password is None:
        verify_password(plain_password, DUMMY_HASH)
        return False
    return verify_password(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create HS256 JWT token with 7-day expiration per PRD §7."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)
    to_encode.update({"iat": now, "exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate HS256 JWT token."""
    return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
