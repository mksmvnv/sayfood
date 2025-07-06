from pathlib import Path

import yaml
from pydantic import BaseModel


class Auth(BaseModel):
    """Auth settings."""

    private_key: Path
    public_key: Path


class Database(BaseModel):
    """Database settings."""

    url: str


class Settings(BaseModel):
    """Base settings."""

    auth: Auth
    db: Database

    @classmethod
    def from_yaml(cls, path: Path) -> None:
        """Parse yaml file data."""
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


settings = Settings.from_yaml(
    Path(__file__).parent / "config.yaml",
)
