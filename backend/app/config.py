from functools import lru_cache
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENV: str = "development"
    JWT_SECRET: str = "supersecretjwtkeyforairbnbcloneproductionmustbe32charsorlonger!"
    DATABASE_URL: str = "sqlite:///./app.db"
    COOKIE_SECURE: bool = False
    FRONTEND_ORIGIN: str = "http://localhost:3000"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CLOUDINARY_URL: str | None = None
    UPLOAD_DIR: str = str(Path(__file__).resolve().parent.parent / "uploads")

    @field_validator("JWT_SECRET")
    @classmethod
    def validate_jwt_secret(cls, v: str, info) -> str:
        # Enforce minimum length in production guard
        if len(v) < 32:
            raise ValueError("JWT_SECRET must be at least 32 characters long")
        return v


@lru_cache
def get_settings() -> Settings:
    return Settings()
