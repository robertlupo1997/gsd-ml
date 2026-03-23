"""Baseline computation for deep learning domains.

Computes random-guess and most-frequent baselines for classification metrics,
and theoretical cross-entropy bounds for loss metrics.
No torch imports -- uses only numpy, math, and sklearn.
"""

from __future__ import annotations

import math

import numpy as np
from sklearn.dummy import DummyClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score


def compute_baselines(
    labels: np.ndarray,
    scoring: str = "accuracy",
    task: str = "image_classification",
) -> dict[str, dict[str, float]]:
    """Compute baselines for deep learning classification tasks.

    For classification metrics (accuracy, f1, f1_weighted): uses sklearn
    DummyClassifier with 'uniform' (random) and 'most_frequent' strategies,
    cross-validated on dummy features.

    For loss metric: returns theoretical random-guess cross-entropy and a
    slightly-better uniform prediction baseline.

    Args:
        labels: Array of class labels.
        scoring: Metric name ('accuracy', 'f1', 'f1_weighted', 'loss').
        task: Task type (e.g. 'image_classification', 'text_classification').

    Returns:
        Dict mapping strategy name to dict with 'score' and 'std'.
    """
    num_classes = len(np.unique(labels))

    if scoring == "loss":
        random_ce = -math.log(1 / num_classes)
        return {
            "random_guess": {"score": random_ce, "std": 0.0},
            "uniform_prediction": {"score": 0.95 * random_ce, "std": 0.0},
        }

    # Classification metrics: use DummyClassifier with cross-validation
    X_dummy = np.zeros((len(labels), 1))
    n_splits = min(5, num_classes)

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    strategies = {
        "random": DummyClassifier(strategy="uniform", random_state=42),
        "most_frequent": DummyClassifier(strategy="most_frequent"),
    }

    baselines = {}
    for name, model in strategies.items():
        scores = cross_val_score(model, X_dummy, labels, scoring=scoring, cv=cv)
        baselines[name] = {"score": float(scores.mean()), "std": float(scores.std())}

    return baselines


def passes_baseline_gate(
    metric_value: float,
    baselines: dict[str, dict[str, float]],
    direction: str,
) -> bool:
    """Check if a metric value beats ALL baselines.

    Args:
        metric_value: The metric value to check.
        baselines: Dict from compute_baselines() output.
        direction: 'maximize' or 'minimize'.

    Returns:
        True only if metric strictly beats every baseline score.
    """
    for baseline_info in baselines.values():
        baseline_score = baseline_info["score"]
        if direction == "maximize" and metric_value <= baseline_score:
            return False
        if direction == "minimize" and metric_value >= baseline_score:
            return False
    return True
