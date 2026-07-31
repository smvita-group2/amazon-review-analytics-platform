"""
Configuration Loader

Loads the project configuration from config/settings.yaml
and exposes it to the entire ML pipeline.
"""

from pathlib import Path

import yaml

# ==========================================================
# Configuration Path
# ==========================================================

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "settings.yaml"

# ==========================================================
# Configuration Loader
# ==========================================================


def load_settings() -> dict:
    """
    Load project settings from YAML.
    """

    with open(
        CONFIG_PATH,
        "r",
        encoding="utf-8",
    ) as file:

        return yaml.safe_load(file)


# ==========================================================
# Global Settings
# ==========================================================

settings = load_settings()

# ==========================================================
# Helper
# ==========================================================


def get_setting(*keys):
    """
    Retrieve nested configuration values.

    Example:
        get_setting("aws", "bucket_name")
        get_setting("embedding", "model_name")
    """

    value = settings

    for key in keys:
        value = value[key]

    return value
