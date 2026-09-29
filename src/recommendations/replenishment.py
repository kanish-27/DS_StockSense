"""Risk categorization and replenishment recommendations — owned by Student 3.

Responsibility:
    Turn forecasts and stock-out risk scores into actionable output:
    assign risk categories and suggest replenishment actions/quantities
    that the dashboard can display.

Status:
    Placeholder only. Risk thresholds, recommendation rules, and any business
    constraints (lead times, safety stock, etc.) have NOT been decided and
    must not be assumed. Implementation depends on confirming the dataset
    schema and team agreements.
"""


def categorize_risk(stockout_probability):
    """Map a stock-out probability to a risk category.

    TODO(team): agree category names and thresholds; store them in config.
    """
    raise NotImplementedError("Risk categorization not implemented yet.")


def recommend_replenishment(forecast, current_stock, risk_category):
    """Suggest a replenishment action for one item.

    TODO(Student 3): define rules only from fields actually present in the data.
    """
    raise NotImplementedError("Replenishment recommendation not implemented yet.")


if __name__ == "__main__":
    print("TODO: replenishment module not implemented yet.")
