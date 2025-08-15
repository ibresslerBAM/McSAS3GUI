from importlib.resources import files
from pathlib import Path


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
    return files("mcsas3gui")


def is_base_path(base_path, full_path):
    # Convert to Path objects
    base = Path(base_path).resolve()
    full = Path(full_path).resolve()

    # Check if the base path is part of the full path
    return base in full.parents or base == full


def make_out_path(inpath, temp_dir: Path):
    outdir = inpath.parent
    if is_base_path(get_main_path(), inpath):
        outdir = temp_dir
    return outdir / (inpath.stem + "_output.hdf5")
