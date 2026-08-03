from pathlib import Path
from typing import Literal

from pydantic import BaseModel, SecretStr

from src.shared.loaders import yaml_loader


class ApplicationSettings(BaseModel):
    """Application settings."""

    title: str
    cors_origins: list[str]


class CookieSettings(BaseModel):
    """Cookie settings."""

    name: str
    httponly: bool
    max_age: int  # Seconds
    samesite: Literal["lax", "strict", "none"] = "lax"
    secure: bool = False


class DatabaseSettings(BaseModel):
    """Database settings."""

    url: SecretStr
    driver: str
    dialect: str
    user: str
    password: SecretStr
    host: str
    port: int
    name: str


class LLMProviderSettings(BaseModel):
    """LLM Provider settings."""

    url: str
    api_key: SecretStr
    model: str
    timeout: int  # Seconds


class Settings(BaseModel):
    """Main settings."""

    app: ApplicationSettings
    cookie: CookieSettings
    db: DatabaseSettings
    llm: LLMProviderSettings


def get_settings() -> Settings:
    """Get settings from yaml file."""
    settings_path = Path(__file__).resolve().parents[3] / ".config" / "settings.yaml"
    settings_data = yaml_loader(settings_path)
    return Settings(**settings_data)


settings = get_settings()
