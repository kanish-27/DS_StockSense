"""7-day demand forecasting — owned by Student 2 (ML Engineer).

Responsibility:
    Engineer features from the cleaned master dataset, train and compare
    forecasting models for a 7-day horizon, validate them with time-aware
    splits (no random shuffling / no future leakage), and save the chosen
    model plus its evaluation results.

Status:
    Placeholder only. Implementation depends on the agreed master dataset from
    Student 1 (date column, demand target, identifiers) and on team agreement
    on evaluation metrics and forecast output format.
"""

from src.common import config


def load_master_dataset():
    """Load the cleaned master dataset produced by Student 1.

    TODO(Student 2): use the agreed path from ``config`` once it is defined.
    """
    raise NotImplementedError("Master dataset loading not implemented yet.")


def build_features(df):
    """Create forecasting features (e.g. lags, rolling stats, calendar features).

    TODO(Student 2): choose features only after confirming available columns.
    """
    raise NotImplementedError("Feature engineering not implemented yet.")


def time_aware_split(df):
    """Split data chronologically for validation (e.g. rolling-origin / TimeSeriesSplit).

    TODO(Student 2): agree the validation window with the team.
    """
    raise NotImplementedError("Time-aware validation not implemented yet.")


def train_and_compare_models(features):
    """Train a simple baseline plus candidate models and compare them.

    TODO(Student 2): always include a naive baseline for comparison.
    """
    raise NotImplementedError("Model training not implemented yet.")


def evaluate_forecast(y_true, y_pred):
    """Compute agreed forecast metrics.

    TODO(Student 2): confirm metrics with the team (e.g. MAE, RMSE, MAPE/sMAPE).
    """
    raise NotImplementedError("Forecast evaluation not implemented yet.")


def main():
    """Run the forecasting pipeline end-to-end."""
    print(f"Forecast horizon: {config.FORECAST_HORIZON_DAYS} days")
    print(f"Models dir:       {config.MODELS_DIR}")
    print("TODO: forecasting pipeline not implemented yet.")


if __name__ == "__main__":
    main()
