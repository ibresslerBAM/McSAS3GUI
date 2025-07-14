import os
from pathlib import Path


def get_default_config_files(directory: Path) -> list[str]:
    """Get a list of YAML configuration files in the specified directory."""
    config_dir = Path(directory)
    if not config_dir.exists():
        config_dir.mkdir(parents=True)  # Create directory if it doesn't exist
    return [str(file.name) for file in config_dir.glob("*.yaml") if file.is_file()]


def get_main_path() -> Path:
    """Get the main path of the application."""
    # Assuming the main path is the directory of this file
    return Path(__file__).resolve().parents[3]