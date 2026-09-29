"""Synthetic dataset generator for STOCKSENSE.

Creates five related CSV files that imitate a fictional multi-store grocery
chain in India:

    stores.csv, products.csv, external_factors.csv, inventory.csv, transactions.csv

IMPORTANT: this data is SYNTHETIC. It is produced from hand-written rules plus
random noise, so it is suitable for building and testing the pipeline — not for
drawing real business conclusions. All store names, brands and suppliers are
fictional; holiday dates are approximate.

How the simulation works (short version):
    daily demand = base demand x store size x weekday x trend x weather effect
                   x festival effect x promotion lift x local event x random noise
    units_sold   = min(demand, stock available)
    Stores reorder when stock + open orders fall to a fixed reorder point.
    Suppliers are sometimes late or deliver partially, and fixed reorder points
    do not adapt to seasonal peaks or promotions -> realistic stock-outs.

A small number of data-quality issues are injected on purpose so the
data-cleaning step has real work to do (see data/synthetic/README.md).
Use --no-quality-issues to generate a clean version.

Usage (from the project root):
    python -m src.data.generate_synthetic_data
    python -m src.data.generate_synthetic_data --seed 7 --no-quality-issues
"""

import argparse
import math
from pathlib import Path

import numpy as np
import pandas as pd

from src.common import config

START_DATE = "2024-01-01"
END_DATE = "2025-12-31"
PRICE_REVISION_DATE = "2025-04-01"

# ---------------------------------------------------------------------------
# Master data definitions (all names are fictional)
# ---------------------------------------------------------------------------
# store_id, city, region, store_type
STORES = [
    ("S001", "Chennai", "South", "Hypermarket"),
    ("S002", "Chennai", "South", "Express"),
    ("S003", "Bengaluru", "South", "Supermarket"),
    ("S004", "Hyderabad", "South", "Supermarket"),
    ("S005", "Mumbai", "West", "Hypermarket"),
    ("S006", "Pune", "West", "Express"),
    ("S007", "Delhi", "North", "Hypermarket"),
    ("S008", "Jaipur", "North", "Supermarket"),
    ("S009", "Lucknow", "North", "Express"),
    ("S010", "Kolkata", "East", "Supermarket"),
]
STORE_TYPE_SIZE_SQFT = {"Hypermarket": (40000, 60000), "Supermarket": (12000, 25000), "Express": (2000, 5000)}
STORE_TYPE_DEMAND = {"Hypermarket": 2.2, "Supermarket": 1.0, "Express": 0.45}

# category -> (supplier_id, nominal lead time in days)
CATEGORY_SUPPLY = {
    "Dairy": ("SUP01", 1),
    "Fresh Produce": ("SUP02", 1),
    "Frozen": ("SUP03", 3),
    "Beverages": ("SUP04", 3),
    "Snacks": ("SUP05", 4),
    "Staples": ("SUP06", 5),
    "Personal Care": ("SUP07", 6),
    "Household": ("SUP08", 6),
}

# name, category, brand, price_inr, shelf_life_days, base_daily_demand, season_type
# base_daily_demand is for a reference "Supermarket"; season_type drives demand
# sensitivity: summer (heat), winter (cold), monsoon (rain), festival, none.
PRODUCTS = [
    ("Toned Milk 1L", "Dairy", "DailyDairy", 56, 3, 45, "none"),
    ("Curd 500g", "Dairy", "DailyDairy", 40, 7, 25, "summer"),
    ("Paneer 200g", "Dairy", "DailyDairy", 90, 10, 10, "festival"),
    ("Butter 100g", "Dairy", "GoldenChurn", 58, 90, 8, "none"),
    ("Cheese Slices 200g", "Dairy", "GoldenChurn", 140, 120, 5, "none"),
    ("Eggs 12pc", "Dairy", "FarmNest", 84, 14, 15, "winter"),
    ("Cola 750ml", "Beverages", "FizzUp", 45, 180, 18, "summer"),
    ("Mango Juice 1L", "Beverages", "SunOrchard", 110, 180, 8, "summer"),
    ("Packaged Water 1L", "Beverages", "PureSip", 20, 365, 30, "summer"),
    ("Green Tea 25 bags", "Beverages", "LeafLine", 160, 540, 4, "none"),
    ("Instant Coffee 100g", "Beverages", "BrewHouse", 310, 540, 3, "winter"),
    ("Potato Chips 52g", "Snacks", "CrunchCo", 20, 120, 30, "none"),
    ("Salted Peanuts 200g", "Snacks", "CrunchCo", 60, 180, 7, "none"),
    ("Cream Biscuits 150g", "Snacks", "BakeWell", 35, 180, 25, "none"),
    ("Namkeen Mix 400g", "Snacks", "SpiceTrail", 110, 150, 6, "festival"),
    ("Chocolate Bar 50g", "Snacks", "CocoaJoy", 50, 270, 12, "festival"),
    ("Instant Noodles 4-pack", "Snacks", "QuickBowl", 56, 270, 14, "monsoon"),
    ("Basmati Rice 5kg", "Staples", "HarvestGold", 650, 540, 4, "none"),
    ("Wheat Atta 5kg", "Staples", "HarvestGold", 290, 90, 6, "none"),
    ("Toor Dal 1kg", "Staples", "HarvestGold", 170, 270, 8, "none"),
    ("Sunflower Oil 1L", "Staples", "SunPress", 155, 270, 10, "festival"),
    ("Sugar 1kg", "Staples", "SweetLeaf", 48, 365, 12, "festival"),
    ("Iodised Salt 1kg", "Staples", "SeaPure", 28, 730, 6, "none"),
    ("Vanilla Ice Cream 1L", "Frozen", "ChillBox", 220, 180, 6, "summer"),
    ("Frozen Peas 500g", "Frozen", "ChillBox", 95, 365, 4, "none"),
    ("Frozen Paratha 5pc", "Frozen", "ChillBox", 120, 180, 4, "none"),
    ("Tomatoes 1kg", "Fresh Produce", "Local Farms", 40, 5, 20, "none"),
    ("Onions 1kg", "Fresh Produce", "Local Farms", 45, 20, 22, "none"),
    ("Bananas 1 dozen", "Fresh Produce", "Local Farms", 60, 4, 15, "none"),
    ("Apples 1kg", "Fresh Produce", "Local Farms", 180, 21, 7, "winter"),
    ("Bath Soap 4x100g", "Personal Care", "GlowCare", 180, 1095, 6, "none"),
    ("Shampoo 340ml", "Personal Care", "GlowCare", 320, 1095, 3, "none"),
    ("Toothpaste 150g", "Personal Care", "BrightSmile", 110, 730, 6, "none"),
    ("Hand Wash 200ml", "Personal Care", "GlowCare", 99, 730, 4, "monsoon"),
    ("Sunscreen SPF50 100ml", "Personal Care", "GlowCare", 350, 730, 2, "summer"),
    ("Dishwash Liquid 500ml", "Household", "SparkleHome", 115, 730, 5, "none"),
    ("Detergent Powder 1kg", "Household", "SparkleHome", 130, 730, 6, "festival"),
    ("Floor Cleaner 1L", "Household", "SparkleHome", 190, 730, 3, "festival"),
    ("Mosquito Repellent Refill", "Household", "NightGuard", 85, 730, 4, "monsoon"),
    ("Decorative Candles 6pc", "Household", "LumiCraft", 150, 1095, 2, "festival"),
]
# Small-format Express stores do not carry these
EXPRESS_EXCLUDED_CATEGORIES = {"Frozen"}
EXPRESS_EXCLUDED_PRODUCTS = {"Basmati Rice 5kg", "Wheat Atta 5kg", "Decorative Candles 6pc"}

# region -> (mean temperature C, seasonal amplitude C, day-of-year of peak heat, base fuel price INR)
REGION_CLIMATE = {
    "South": (29.0, 3.0, 130, 101.5),
    "West": (28.0, 4.0, 130, 104.2),
    "North": (25.0, 9.0, 165, 95.0),
    "East": (27.0, 6.0, 140, 103.9),
}
REGIONS = list(REGION_CLIMATE)
ALL = tuple(REGIONS)

# date, name, regions observing it, festival shopping intensity (0 = no shopping spike).
# Dates are approximate and used only for simulation.
HOLIDAYS = [
    ("2024-01-15", "Pongal / Makar Sankranti", ("South",), 0.8),
    ("2024-01-26", "Republic Day", ALL, 0.0),
    ("2024-03-25", "Holi", ("North", "West", "East"), 0.8),
    ("2024-04-11", "Eid al-Fitr", ALL, 0.6),
    ("2024-08-15", "Independence Day", ALL, 0.0),
    ("2024-09-07", "Ganesh Chaturthi", ("West", "South"), 0.7),
    ("2024-10-02", "Gandhi Jayanti", ALL, 0.0),
    ("2024-10-12", "Dussehra", ALL, 0.8),
    ("2024-11-01", "Diwali", ALL, 1.5),
    ("2024-12-25", "Christmas", ALL, 0.6),
    ("2025-01-14", "Pongal / Makar Sankranti", ("South",), 0.8),
    ("2025-01-26", "Republic Day", ALL, 0.0),
    ("2025-03-14", "Holi", ("North", "West", "East"), 0.8),
    ("2025-03-31", "Eid al-Fitr", ALL, 0.6),
    ("2025-08-15", "Independence Day", ALL, 0.0),
    ("2025-08-27", "Ganesh Chaturthi", ("West", "South"), 0.7),
    ("2025-10-02", "Dussehra / Gandhi Jayanti", ALL, 0.8),
    ("2025-10-20", "Diwali", ALL, 1.5),
    ("2025-12-25", "Christmas", ALL, 0.6),
]

WEEKDAY_FACTOR = np.array([0.92, 0.90, 0.93, 0.97, 1.05, 1.20, 1.13])  # Mon..Sun
ANNUAL_GROWTH = 0.08
NOISE_SHAPE = 6.0  # gamma-Poisson dispersion (lower = noisier)
PROMO_START_PROB = 1 / 45
PROMO_DISCOUNTS = [0.05, 0.10, 0.15, 0.20, 0.25]
PROMO_LIFT_PER_DISCOUNT = 2.0  # 20% off -> 1.4x demand
SUPPLIER_DELAY_PROB = 0.12
PARTIAL_DELIVERY_PROB = 0.05


# ---------------------------------------------------------------------------
# Master tables
# ---------------------------------------------------------------------------
def build_stores(rng):
    rows = []
    for store_id, city, region, store_type in STORES:
        low, high = STORE_TYPE_SIZE_SQFT[store_type]
        opening = pd.Timestamp("2012-01-01") + pd.Timedelta(days=int(rng.integers(0, 365 * 10)))
        rows.append({
            "store_id": store_id,
            "store_name": f"StockSense Mart {city} {store_id[-2:]}",
            "city": city,
            "region": region,
            "store_type": store_type,
            "size_sqft": int(round(rng.integers(low, high) / 100) * 100),
            "opening_date": opening.strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)


def build_products():
    rows = []
    for i, (name, category, brand, price, shelf_life, _, _) in enumerate(PRODUCTS, start=1):
        supplier_id, lead_time = CATEGORY_SUPPLY[category]
        rows.append({
            "product_id": f"P{i:03d}",
            "product_name": name,
            "category": category,
            "brand": brand,
            "base_price_inr": float(price),
            "unit_cost_inr": round(price * 0.72, 2),
            "is_perishable": int(shelf_life <= 14),
            "shelf_life_days": shelf_life,
            "supplier_id": supplier_id,
            "supplier_lead_time_days": lead_time,
        })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# External factors (per region per day)
# ---------------------------------------------------------------------------
def festival_proximity(dates, region):
    """Shopping intensity from 0 up to the festival's intensity, peaking the day before."""
    prox = np.zeros(len(dates))
    for day, _, regions, intensity in HOLIDAYS:
        if intensity == 0 or region not in regions:
            continue
        days_before = np.asarray((pd.Timestamp(day) - dates).days)
        weight = np.where((days_before >= 1) & (days_before <= 7), (8 - days_before) / 7, 0.0)
        weight = np.where(days_before == 0, 0.3, weight)
        prox = np.maximum(prox, intensity * weight)
    return prox


def build_external_factors(dates, rng):
    doy = dates.dayofyear.to_numpy()
    month = dates.month.to_numpy()
    frames, prox_by_region = [], {}
    for region, (mean_t, amp, peak, fuel_base) in REGION_CLIMATE.items():
        temp = mean_t + amp * np.cos(2 * np.pi * (doy - peak) / 365) + rng.normal(0, 1.5, len(dates))

        rain_prob = np.where((month >= 6) & (month <= 9), 0.6, 0.08)
        rain_scale = np.where((month >= 6) & (month <= 9), 14.0, 5.0)
        if region == "South":  # north-east monsoon
            rain_prob = np.where((month >= 10) & (month <= 12), 0.45, rain_prob)
            rain_scale = np.where((month >= 10) & (month <= 12), 12.0, rain_scale)
        rain = np.where(rng.random(len(dates)) < rain_prob, rng.exponential(rain_scale), 0.0)
        temp = temp - 0.04 * rain  # rainy days are a little cooler

        holiday_name = np.full(len(dates), "", dtype=object)
        for day, name, regions, _ in HOLIDAYS:
            if region in regions:
                holiday_name[dates == pd.Timestamp(day)] = name

        fuel = fuel_base + np.cumsum(rng.normal(0.004, 0.03, len(dates)))
        prox_by_region[region] = festival_proximity(dates, region)

        frames.append(pd.DataFrame({
            "date": dates,
            "region": region,
            "temperature_c": np.round(temp, 1),
            "precipitation_mm": np.round(rain, 1),
            "is_holiday": (holiday_name != "").astype(int),
            "holiday_name": holiday_name,
            "local_event": (rng.random(len(dates)) < 0.015).astype(int),
            "fuel_price_inr": np.round(fuel, 2),
        }))
    return pd.concat(frames, ignore_index=True), prox_by_region


# ---------------------------------------------------------------------------
# Demand + inventory simulation
# ---------------------------------------------------------------------------
def build_store_product_pairs(stores, products):
    pairs = []
    for s_idx, store in stores.iterrows():
        for p_idx, product in products.iterrows():
            if store["store_type"] == "Express" and (
                product["category"] in EXPRESS_EXCLUDED_CATEGORIES
                or product["product_name"] in EXPRESS_EXCLUDED_PRODUCTS
            ):
                continue
            pairs.append((s_idx, p_idx))
    return pairs


def simulate_promotions(n_days, n_pairs, rng):
    discount = np.zeros((n_days, n_pairs))
    for j in range(n_pairs):
        t = 0
        while t < n_days:
            if rng.random() < PROMO_START_PROB:
                length = int(rng.integers(3, 8))
                discount[t:t + length, j] = rng.choice(PROMO_DISCOUNTS, p=[0.15, 0.3, 0.25, 0.2, 0.1])
                t += length + 7  # cool-down between promotions
            else:
                t += 1
    return discount


def simulate(stores, products, dates, external, prox_by_region, rng):
    pairs = build_store_product_pairs(stores, products)
    n_days, n_pairs = len(dates), len(pairs)
    s_idx = np.array([p[0] for p in pairs])
    p_idx = np.array([p[1] for p in pairs])

    season = np.array([PRODUCTS[i][6] for i in p_idx])
    base = np.array([PRODUCTS[i][5] for i in p_idx], dtype=float)
    store_mult = np.array([STORE_TYPE_DEMAND[t] for t in stores["store_type"]]) * rng.uniform(0.85, 1.15, len(stores))
    affinity = rng.lognormal(0, 0.2, n_pairs)
    level = base * store_mult[s_idx] * affinity  # average daily demand level per pair

    # Region-level daily drivers, expanded to [day, pair]
    region_of_pair = stores["region"].to_numpy()[s_idx]
    ext = external.set_index(["region", "date"])
    temp = np.column_stack([ext.loc[r, "temperature_c"].to_numpy() for r in region_of_pair])
    rain = np.column_stack([ext.loc[r, "precipitation_mm"].to_numpy() for r in region_of_pair])
    event = np.column_stack([ext.loc[r, "local_event"].to_numpy() for r in region_of_pair])
    prox = np.column_stack([prox_by_region[r] for r in region_of_pair])
    rain_7d = pd.DataFrame(rain).rolling(7, min_periods=1).mean().to_numpy()

    weekday = WEEKDAY_FACTOR[dates.weekday.to_numpy()][:, None]
    trend = (1 + ANNUAL_GROWTH * np.arange(n_days) / 365)[:, None]

    weather = np.ones((n_days, n_pairs))
    weather = np.where(season == "summer", np.clip(1 + 0.05 * (temp - 28), 0.6, 1.8), weather)
    weather = np.where(season == "winter", np.clip(1 + 0.02 * (25 - temp), 0.8, 1.4), weather)
    weather = np.where(season == "monsoon", np.clip(1 + 0.03 * rain_7d, 1.0, 2.0), weather)
    footfall = np.clip(1 - 0.004 * rain, 0.8, 1.0)  # heavy rain keeps shoppers home

    festival = 1 + 0.15 * prox + np.where(season == "festival", 1.0, 0.0) * prox
    category = np.array([PRODUCTS[i][1] for i in p_idx])
    event_boost = np.where(np.isin(category, ["Snacks", "Beverages"]), 1.25, 1.05)
    event_mult = np.where(event == 1, event_boost, 1.0)

    discount = simulate_promotions(n_days, n_pairs, rng)
    promo_lift = 1 + PROMO_LIFT_PER_DISCOUNT * discount

    mean_demand = level * weekday * trend * weather * footfall * festival * event_mult * promo_lift
    demand = rng.poisson(mean_demand * rng.gamma(NOISE_SHAPE, 1 / NOISE_SHAPE, mean_demand.shape))

    # Prices: one revision per product during the period
    base_price = np.array([PRODUCTS[i][3] for i in p_idx], dtype=float)
    revision = rng.uniform(1.0, 1.08, len(products))[p_idx]
    after_revision = np.asarray(dates >= pd.Timestamp(PRICE_REVISION_DATE))[:, None]
    unit_price = np.where(after_revision, np.round(base_price * revision), base_price)

    # Inventory policy: fixed reorder point / order-up-to level per pair
    shelf_life = np.array([PRODUCTS[i][4] for i in p_idx])
    perishable = shelf_life <= 14
    lead = np.array([CATEGORY_SUPPLY[PRODUCTS[i][1]][1] for i in p_idx])
    avg_demand = level * (1 + ANNUAL_GROWTH / 2)
    safety_days = np.where(perishable, rng.uniform(0.5, 1.5, n_pairs), rng.uniform(1.0, 3.5, n_pairs))
    cycle_days = np.where(perishable, 2, 7)
    reorder_point = np.maximum(1, np.ceil(avg_demand * (lead + safety_days))).astype(int)
    order_up_to = reorder_point + np.maximum(1, np.ceil(avg_demand * cycle_days)).astype(int)

    stock = order_up_to.copy()
    arrivals = np.zeros((n_days + 20, n_pairs), dtype=int)
    on_order = np.zeros(n_pairs, dtype=int)
    cols = {k: np.zeros((n_days, n_pairs), dtype=int) for k in
            ["opening_stock", "units_received", "units_sold", "closing_stock", "units_ordered"]}

    for t in range(n_days):
        received = arrivals[t]
        on_order -= received
        available = stock + received
        sold = np.minimum(demand[t], available)
        closing = available - sold

        position = closing + on_order
        needs_order = position <= reorder_point
        qty = np.where(needs_order, order_up_to - position, 0)
        delay = np.where(rng.random(n_pairs) < SUPPLIER_DELAY_PROB, rng.integers(1, 5, n_pairs), 0)
        partial = np.where(rng.random(n_pairs) < PARTIAL_DELIVERY_PROB, rng.uniform(0.5, 0.9, n_pairs), 1.0)
        delivered = np.floor(qty * partial).astype(int)
        arrive_at = t + lead + delay
        np.add.at(arrivals, (arrive_at[needs_order], np.flatnonzero(needs_order)), delivered[needs_order])
        on_order += np.where(needs_order, delivered, 0)

        cols["opening_stock"][t] = stock
        cols["units_received"][t] = received
        cols["units_sold"][t] = sold
        cols["closing_stock"][t] = closing
        cols["units_ordered"][t] = qty
        stock = closing

    store_ids = stores["store_id"].to_numpy()[s_idx]
    product_ids = products["product_id"].to_numpy()[p_idx]
    long = lambda a: a.reshape(-1)  # day-major flattening matches np.repeat/np.tile below
    inventory = pd.DataFrame({
        "date": np.repeat(dates, n_pairs),
        "store_id": np.tile(store_ids, n_days),
        "product_id": np.tile(product_ids, n_days),
        **{k: long(v) for k, v in cols.items() if k != "units_ordered"},
        "reorder_point": np.tile(reorder_point, n_days),
        "units_ordered": long(cols["units_ordered"]),
    })
    inventory["stockout_flag"] = (inventory["closing_stock"] == 0).astype(int)

    sales = pd.DataFrame({
        "date": inventory["date"],
        "store_id": inventory["store_id"],
        "product_id": inventory["product_id"],
        "units_sold": inventory["units_sold"],
        "unit_price_inr": long(unit_price),
        "discount_pct": np.round(long(discount) * 100).astype(int),
    })
    sales = sales[sales["units_sold"] > 0].reset_index(drop=True)
    sales["promo_flag"] = (sales["discount_pct"] > 0).astype(int)
    sales["revenue_inr"] = np.round(sales["units_sold"] * sales["unit_price_inr"] * (1 - sales["discount_pct"] / 100), 2)
    sales.insert(0, "transaction_id", [f"TXN{i:07d}" for i in range(1, len(sales) + 1)])
    return inventory, sales


# ---------------------------------------------------------------------------
# Deliberate data-quality issues (documented in data/synthetic/README.md)
# ---------------------------------------------------------------------------
def inject_quality_issues(tables, rng):
    stores, products = tables["stores"], tables["products"]
    external, inventory, transactions = tables["external_factors"], tables["inventory"], tables["transactions"]

    stores.loc[stores["store_id"] == "S002", "city"] = " chennai"
    products.loc[rng.choice(products.index, 2, replace=False), "brand"] = np.nan

    for col in ["temperature_c", "precipitation_mm"]:
        external.loc[rng.choice(external.index, int(0.01 * len(external)), replace=False), col] = np.nan

    inventory["closing_stock"] = inventory["closing_stock"].astype("Int64")
    inventory.loc[rng.choice(inventory.index, int(0.002 * len(inventory)), replace=False), "closing_stock"] = pd.NA

    transactions.loc[rng.choice(transactions.index, int(0.001 * len(transactions)), replace=False), "unit_price_inr"] = np.nan
    dupes = transactions.loc[rng.choice(transactions.index, int(0.002 * len(transactions)), replace=False)]
    tables["transactions"] = (
        pd.concat([transactions, dupes]).sort_values(["date", "store_id", "product_id"], kind="stable").reset_index(drop=True)
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def generate(seed=config.RANDOM_SEED, quality_issues=True):
    """Generate all five tables and return them as a dict of DataFrames."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(START_DATE, END_DATE, freq="D")
    stores = build_stores(rng)
    products = build_products()
    external, prox_by_region = build_external_factors(dates, rng)
    inventory, transactions = simulate(stores, products, dates, external, prox_by_region, rng)

    tables = {
        "stores": stores,
        "products": products,
        "external_factors": external,
        "inventory": inventory,
        "transactions": transactions,
    }
    if quality_issues:
        inject_quality_issues(tables, rng)
    return tables


def save(tables, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, df in tables.items():
        df = df.copy()
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        path = output_dir / f"{name}.csv"
        df.to_csv(path, index=False)
        print(f"  {path.name:<22} {len(df):>9,} rows  {path.stat().st_size / 1e6:6.1f} MB")


def main():
    parser = argparse.ArgumentParser(description="Generate the STOCKSENSE synthetic dataset.")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED)
    parser.add_argument("--output-dir", default=config.SYNTHETIC_DATA_DIR)
    parser.add_argument("--no-quality-issues", action="store_true", help="skip injected data-quality issues")
    args = parser.parse_args()

    print(f"Generating synthetic data (seed={args.seed}) -> {args.output_dir}")
    tables = generate(seed=args.seed, quality_issues=not args.no_quality_issues)
    save(tables, args.output_dir)

    inv = tables["inventory"]
    print(f"Stock-out rate (closing_stock == 0): {inv['stockout_flag'].mean():.2%}")


if __name__ == "__main__":
    main()
