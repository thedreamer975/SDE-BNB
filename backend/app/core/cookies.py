from fastapi import Response
from app.config import get_settings

settings = get_settings()

COOKIE_NAME = "session"
COOKIE_MAX_AGE = 7 * 24 * 60 * 60  # 7 days (604800 seconds)


def set_auth_cookie(response: Response, token: str) -> None:
    """
    Set httpOnly authentication cookie per PRD §7:
    HttpOnly; Secure (prod); SameSite=Lax; Path=/; Max-Age=604800
    """
    secure = settings.COOKIE_SECURE or (settings.ENV == "production")
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def clear_auth_cookie(response: Response) -> None:
    """Clear authentication cookie upon logout."""
    secure = settings.COOKIE_SECURE or (settings.ENV == "production")
    response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
