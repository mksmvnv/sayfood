from pathlib import Path
from typing import Any

import yaml


def yaml_loader(path: Path) -> dict[str, Any]:
    """Load data from yaml file."""
    if not path.exists():
        raise FileNotFoundError(f"YAML file not found: {path}")

    with open(path) as file:
        data = yaml.safe_load(file)
        return data or {}
