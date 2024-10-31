import os
from pathlib import Path

def get_default_config_files(directory="read_configurations"):
    """Get a list of YAML configuration files in the specified directory."""
    config_dir = Path(directory)
    if not config_dir.exists():
        config_dir.mkdir(parents=True)  # Create directory if it doesn't exist
    return [str(file.name) for file in config_dir.glob("*.yaml") if file.is_file()]
