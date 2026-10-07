from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    avatar_url: str | None = None
    is_superhost: bool = False
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("is_superhost", mode="before")
    @classmethod
    def convert_superhost(cls, v: Any) -> bool:
        return bool(v)


class UpdateUserRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=60)

    @field_validator("name")
    @classmethod
    def sanitize_name(cls, v: str) -> str:
        stripped = v.strip()
        if len(stripped) < 2 or len(stripped) > 60:
            raise ValueError("Name must be between 2 and 60 characters.")
        return stripped
