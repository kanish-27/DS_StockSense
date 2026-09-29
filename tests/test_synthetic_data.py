"""Integrity checks for the synthetic dataset in data/synthetic/.

Skipped automatically if the CSV files have not been generated.

Run from the project root:
    pytest
"""

import pandas as pd
import pytest

from src.common import config

TABLES = ["stores", "products", "external_factors", "inventory", "transactions"]
DATA_DIR = config.SYNTHETIC_DATA_DIR

pytestmark = pytest.mark.skipif(
    not all((DATA_DIR / f"{t}.csv").exists() for t in TABLES),
    reason="synthetic data not generated (run: python -m src.data.generate_synthetic_data)",
)


@pytest.fixture(scope="module")
def data():
    return {t: pd.read_csv(DATA_DIR / f"{t}.csv") for t in TABLES}


def test_ids_are_valid(data):
    stores, products = data["stores"], data["products"]
    for name in ["inventory", "transactions"]:
        assert data[name]["store_id"].isin(stores["store_id"]).all()
        assert data[name]["product_id"].isin(products["product_id"]).all()
    assert data["external_factors"]["region"].isin(stores["region"]).all()


def test_inventory_stock_balance(data):
    inv = data["inventory"].dropna(subset=["closing_stock"])
    expected = inv["opening_stock"] + inv["units_received"] - inv["units_sold"]
    assert (expected == inv["closing_stock"]).all()
    assert (inv["closing_stock"] >= 0).all()


def test_inventory_and_transactions_agree(data):
    tx = data["transactions"].drop_duplicates()
    merged = data["inventory"].merge(
        tx[["date", "store_id", "product_id", "units_sold"]],
        on=["date", "store_id", "product_id"],
        how="left",
        suffixes=("", "_tx"),
    )
    assert (merged["units_sold_tx"].fillna(0) == merged["units_sold"]).all()
