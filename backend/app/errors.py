from typing import Any
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette.exceptions import HTTPException as StarletteHTTPException


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        fields: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.fields = fields or {}


class UnauthenticatedError(AppError):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            code="UNAUTHENTICATED",
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "You do not have permission to perform this action", code: str = "FORBIDDEN"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            code="NOT_FOUND",
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
        )


class ConflictError(AppError):
    def __init__(self, message: str, code: str = "CONFLICT", fields: dict[str, Any] | None = None):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            fields=fields,
        )


class DatesUnavailableError(ConflictError):
    def __init__(self, message: str = "Those dates are no longer available.", fields: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            code="DATES_UNAVAILABLE",
            fields=fields or {"check_in": "Dates overlap with an existing booking"},
        )


class PaymentDeclinedError(AppError):
    def __init__(self, message: str = "Your card was declined."):
        super().__init__(
            code="PAYMENT_DECLINED",
            message=message,
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
        )


class RateLimitedError(AppError):
    def __init__(self, message: str = "Too many attempts. Try again in a minute."):
        super().__init__(
            code="RATE_LIMITED",
            message=message,
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


def make_error_response(code: str, message: str, status_code: int, fields: dict[str, Any] | None = None) -> JSONResponse:
    payload = {
        "error": {
            "code": code,
            "message": message,
            "fields": fields or {},
        }
    }
    return JSONResponse(status_code=status_code, content=payload)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
        return make_error_response(
            code="RATE_LIMITED",
            message="Too many attempts. Try again in a minute.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        return make_error_response(exc.code, exc.message, exc.status_code, exc.fields)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        fields: dict[str, str] = {}
        for err in exc.errors():
            loc = err.get("loc", [])
            field_name = str(loc[-1]) if loc else "body"
            fields[field_name] = err.get("msg", "Invalid value")
        return make_error_response(
            code="VALIDATION_ERROR",
            message="Invalid request data.",
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            fields=fields,
        )

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        code_map = {
            401: "UNAUTHENTICATED",
            403: "FORBIDDEN",
            404: "NOT_FOUND",
            409: "CONFLICT",
            429: "RATE_LIMITED",
        }
        code = code_map.get(exc.status_code, "ERROR")
        detail = exc.detail if isinstance(exc.detail, str) else "An error occurred."
        return make_error_response(code, detail, exc.status_code)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", "unknown")
        # Log internally, return generic error envelope per PRD §8.2 / §11
        return make_error_response(
            code="INTERNAL_ERROR",
            message=f"An internal server error occurred. Request ID: {request_id}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
