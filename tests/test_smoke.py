"""Smoke test: checks that every project module can be imported.

This does NOT test any business logic (none exists yet). It catches broken
imports, syntax errors, and package-structure problems early.

Run from the project root:
    pytest
"""

import importlib

import pytest

MODULES = [
    "src.common.config",
    "src.data.prepare_data",
    "src.data.generate_synthetic_data",
    "src.forecasting.train_forecast",
    "src.classification.train_stockout",
    "src.explainability.explain",
    "src.recommendations.replenishment",
]


@pytest.mark.parametrize("module_name", MODULES)
def test_module_imports(module_name):
    assert importlib.import_module(module_name) is not None


def test_config_paths_point_inside_project():
    from src.common import config

    assert config.PROJECT_ROOT.is_dir()
    assert config.RAW_DATA_DIR.is_relative_to(config.PROJECT_ROOT)
    assert config.PROCESSED_DATA_DIR.is_relative_to(config.PROJECT_ROOT)
    assert config.FORECAST_HORIZON_DAYS == 7
