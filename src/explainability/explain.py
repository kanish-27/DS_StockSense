"""Model explainability — owned by Student 3 (Decision Intelligence Engineer).

Responsibility:
    Explain why the models make their predictions (global feature importance
    and per-item explanations, e.g. with SHAP) in language that business
    users of the dashboard can understand.

Status:
    Placeholder only. Implementation depends on the trained models and the
    final feature set, which are not available yet.
"""


def global_feature_importance(model, features):
    """Summarize which features matter most overall.

    TODO(Student 3): implement after a model has been trained.
    """
    raise NotImplementedError("Global explainability not implemented yet.")


def explain_single_prediction(model, feature_row):
    """Explain one prediction (e.g. one product/location at risk).

    TODO(Student 3): decide how explanations are shown in the dashboard.
    """
    raise NotImplementedError("Local explainability not implemented yet.")


if __name__ == "__main__":
    print("TODO: explainability module not implemented yet.")
