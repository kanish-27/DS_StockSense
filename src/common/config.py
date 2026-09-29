"""Shared project configuration for STOCKSENSE.

Responsibility:
    Single place for paths, constants, and settings that all three roles use,
    so nobody hard-codes file locations in their own module.

Status:
    Paths and generic settings only. Dataset-specific values (file names,
    column names, date column, product/store identifiers, target definitions)
    are NOT defined yet — they depend on confirming the actual dataset schema
    and team agreements. Add them here once agreed, not in individual modules.
"""

import os
from pathlib import Path

# Load optional overrides from a local .env file if python-dotenv is installed.
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv is optional; defaults below still work
    pass

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _path_from_env(var_name: str, default: str) -> Path:
    """Return an absolute path from an env variable, relative to PROJECT_ROOT."""
    return PROJECT_ROOT / os.getenv(var_name, default)


RAW_DATA_DIR = _path_from_env("STOCKSENSE_RAW_DATA_DIR", "data/raw")
PROCESSED_DATA_DIR = _path_from_env("STOCKSENSE_PROCESSED_DATA_DIR", "data/processed")
MODELS_DIR = _path_from_env("STOCKSENSE_MODELS_DIR", "models")
REPORTS_DIR = PROJECT_ROOT / "reports"

# ---------------------------------------------------------------------------
# General settings
# ---------------------------------------------------------------------------
RANDOM_SEED = int(os.getenv("STOCKSENSE_RANDOM_SEED", "42"))

# Forecast horizon stated in the problem statement (7-day demand forecast).
FORECAST_HORIZON_DAYS = 7

# ---------------------------------------------------------------------------
# TODO(team): dataset contract — fill in after Student 1 inspects the raw data
# ---------------------------------------------------------------------------
# MASTER_DATASET_PATH = PROCESSED_DATA_DIR / "<agreed_file_name>"
# DATE_COLUMN = "<to be confirmed>"
# ID_COLUMNS = ["<to be confirmed>"]        # e.g. product / store identifiers
# DEMAND_TARGET_COLUMN = "<to be confirmed>"
# STOCKOUT_TARGET_COLUMN = "<to be confirmed>"  # or how it is derived
# RISK_THRESHOLDS = {...}                   # agreed with Student 3
