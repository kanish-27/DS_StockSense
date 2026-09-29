"""Stock-out risk classification — owned by Student 3 (Decision Intelligence Engineer).

Responsibility:
    Train a classifier that predicts whether an item is at risk of a
    stock-out, evaluate it with time-aware validation, and output risk
    probabilities that feed risk categorization and replenishment logic.

Status:
    Placeholder only. Implementation depends on the agreed master dataset and
    on how "stock-out" is defined for this dataset (an existing label, or a
    rule derived from inventory vs. demand) — this must be agreed by the team.
    It may also use Student 2's demand forecasts as inputs.
"""

from src.common import config


def define_stockout_target(df):
    """Create or select the stock-out label.

    TODO(Student 3): confirm the stock-out definition with the team before coding.
    """
    raise NotImplementedError("Stock-out target definition not implemented yet.")


def train_classifier(features, target):
    """Train and compare stock-out classifiers (include a simple baseline).

    TODO(Student 3): handle class imbalance if stock-outs are rare.
    """
    raise NotImplementedError("Stock-out classifier training not implemented yet.")


def evaluate_classifier(y_true, y_pred, y_proba=None):
    """Compute agreed classification metrics.

    TODO(Student 3): confirm metrics (e.g. recall, precision, F1, PR-AUC).
    """
    raise NotImplementedError("Classifier evaluation not implemented yet.")


def main():
    """Run the stock-out classification pipeline end-to-end."""
    print(f"Random seed: {config.RANDOM_SEED}")
    print("TODO: stock-out classification pipeline not implemented yet.")


if __name__ == "__main__":
    main()
