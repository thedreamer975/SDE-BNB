import re
from pydantic import BaseModel, Field, field_validator
from app.security import validate_password_policy

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)
    email: str
    password: str

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2 or len(stripped) > 60:
            raise ValueError("Name must be between 2 and 60 characters.")
        return stripped

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        stripped = v.strip().lower()
        if not EMAIL_REGEX.match(stripped):
            raise ValueError("Invalid email format.")
        return stripped

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        validate_password_policy(v)
        return v


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def sanitize_email(cls, v: str) -> str:
        stripped = v.strip().lower()
        if not EMAIL_REGEX.match(stripped):
            raise ValueError("Invalid email format.")
        return stripped
