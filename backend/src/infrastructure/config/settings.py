from pathlib import Path

from pydantic import BaseModel, SecretStr

from src.shared.loaders import yaml_loader


class DatabaseSettings(BaseModel):
    """Database settings."""

    driver: str
    dialect: str
    user: str
    password: SecretStr
    host: str
    port: int
    name: str


class Settings(BaseModel):
    """Main settings."""

    db: DatabaseSettings


def get_settings() -> Settings:
    """Get settings from yaml file."""
    settings_path = Path(__file__).resolve().parents[3] / ".config" / "settings.yaml"
    settings_data = yaml_loader(settings_path)
    return Settings(**settings_data)


settings = get_settings()
