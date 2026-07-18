"""
Loads config/settings.yaml so no module hardcodes paths, ports, or
other settings directly. Every other module in this package imports
`load_config` rather than reading the YAML file itself.
"""

from pathlib import Path
import yaml

# Project root is two levels up from this file (src/config.py -> project/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "config" / "settings.yaml"


def load_config(path: Path = CONFIG_PATH) -> dict:
    """Load and return the project's YAML configuration as a dict."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def resolve_path(relative_path: str) -> Path:
    """Turn a config-relative path (e.g. 'data/operator_performance.db')
    into an absolute path based at the project root, so scripts work
    regardless of which directory they're run from."""
    return PROJECT_ROOT / relative_path
