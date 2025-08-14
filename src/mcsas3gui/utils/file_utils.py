from pathlib import Path
from importlib.resources import files


def get_default_config_files(directory: Path) -> list[str]:
    """Get a list of YAML configuration files in the specified directory."""
    config_dir = Path(directory)
    if not config_dir.exists():
        config_dir.mkdir(parents=True)  # Create directory if it doesn't exist
    return [str(file.name) for file in config_dir.glob("*.yaml") if file.is_file()]


def get_main_path() -> Path:
    """Get the main path of the application. See also:
    https://setuptools.pypa.io/en/latest/userguide/datafiles.html#accessing-data-files-at-runtime
    """
    return files('mcsas3gui')
