"""Tests for baseline computation and dual-baseline gate."""

from __future__ import annotations

from sklearn.datasets import make_classification, make_regression

# ---------------------------------------------------------------------------
# compute_baselines
# ---------------------------------------------------------------------------


class TestComputeBaselines:
    """compute_baselines() returns scores for naive and domain-specific strategies."""

    def test_classification_strategies(self):
        from gsd_ml.baselines.tabular import compute_baselines

        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        baselines = compute_baselines(X, y, scoring="accuracy", task="classification")
        assert "most_frequent" in baselines
        assert "stratified" in baselines

    def test_regression_strategies(self):
        from gsd_ml.baselines.tabular import compute_baselines

        X, y = make_regression(n_samples=100, n_features=5, random_state=42)
        baselines = compute_baselines(X, y, scoring="r2", task="regression")
        assert "mean" in baselines
        assert "median" in baselines

    def test_baseline_scores_have_mean_and_std(self):
        from gsd_ml.baselines.tabular import compute_baselines

        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        baselines = compute_baselines(X, y, scoring="accuracy", task="classification")
        for _name, result in baselines.items():
            assert "score" in result
            assert "std" in result
            assert isinstance(result["score"], float)
            assert isinstance(result["std"], float)

    def test_classification_uses_dummy_classifier(self):
        from gsd_ml.baselines.tabular import compute_baselines

        X, y = make_classification(n_samples=100, n_features=5, random_state=42)
        baselines = compute_baselines(X, y, scoring="accuracy", task="classification")
        for result in baselines.values():
            assert 0 <= result["score"] <= 1

    def test_regression_uses_dummy_regressor(self):
        from gsd_ml.baselines.tabular import compute_baselines

        X, y = make_regression(n_samples=100, n_features=5, random_state=42)
        baselines = compute_baselines(X, y, scoring="neg_root_mean_squared_error", task="regression")
        for result in baselines.values():
            assert result["score"] <= 0


# ---------------------------------------------------------------------------
# passes_baseline_gate
# ---------------------------------------------------------------------------


class TestPassesBaselineGate:
    """passes_baseline_gate() returns True only when metric beats ALL baselines."""

    def test_maximize_passes_when_above_all(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {
            "most_frequent": {"score": 0.5, "std": 0.01},
            "stratified": {"score": 0.4, "std": 0.02},
        }
        assert passes_baseline_gate(0.6, baselines, direction="maximize") is True

    def test_maximize_fails_when_below_one(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {
            "most_frequent": {"score": 0.5, "std": 0.01},
            "stratified": {"score": 0.4, "std": 0.02},
        }
        assert passes_baseline_gate(0.45, baselines, direction="maximize") is False

    def test_maximize_fails_when_equal(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {"dummy": {"score": 0.5, "std": 0.01}}
        assert passes_baseline_gate(0.5, baselines, direction="maximize") is False

    def test_minimize_passes_when_below_all(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {
            "mean": {"score": 10.0, "std": 1.0},
            "median": {"score": 12.0, "std": 1.5},
        }
        assert passes_baseline_gate(8.0, baselines, direction="minimize") is True

    def test_minimize_fails_when_above_one(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {
            "mean": {"score": 10.0, "std": 1.0},
            "median": {"score": 12.0, "std": 1.5},
        }
        assert passes_baseline_gate(11.0, baselines, direction="minimize") is False

    def test_minimize_fails_when_equal(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        baselines = {"dummy": {"score": 5.0, "std": 0.5}}
        assert passes_baseline_gate(5.0, baselines, direction="minimize") is False

    def test_empty_baselines_passes(self):
        from gsd_ml.baselines.tabular import passes_baseline_gate

        assert passes_baseline_gate(0.5, {}, direction="maximize") is True


# ---------------------------------------------------------------------------
# DL baselines
# ---------------------------------------------------------------------------


class TestDLBaselines:
    """Deep learning baseline computation and gate."""

    def test_compute_baselines_classification(self):
        import numpy as np
        from gsd_ml.baselines.deeplearning import compute_baselines

        labels = np.array([0, 1, 2, 0, 1, 2, 0, 1, 2, 0])
        baselines = compute_baselines(labels, scoring="accuracy")
        assert "random" in baselines
        assert "most_frequent" in baselines
        for result in baselines.values():
            assert "score" in result
            assert "std" in result

    def test_compute_baselines_loss(self):
        import numpy as np
        from gsd_ml.baselines.deeplearning import compute_baselines

        labels = np.array([0, 1, 2])
        baselines = compute_baselines(labels, scoring="loss")
        assert "random_guess" in baselines
        assert baselines["random_guess"]["score"] > 0

    def test_passes_baseline_gate_maximize_passes(self):
        from gsd_ml.baselines.deeplearning import passes_baseline_gate

        baselines = {"random": {"score": 0.5, "std": 0.01}}
        assert passes_baseline_gate(0.8, baselines, direction="maximize") is True

    def test_passes_baseline_gate_maximize_fails(self):
        from gsd_ml.baselines.deeplearning import passes_baseline_gate

        baselines = {"random": {"score": 0.5, "std": 0.01}}
        assert passes_baseline_gate(0.3, baselines, direction="maximize") is False

    def test_passes_baseline_gate_minimize_passes(self):
        from gsd_ml.baselines.deeplearning import passes_baseline_gate

        baselines = {"random_guess": {"score": 10.0, "std": 0.0}}
        assert passes_baseline_gate(2.0, baselines, direction="minimize") is True

    def test_passes_baseline_gate_minimize_fails(self):
        from gsd_ml.baselines.deeplearning import passes_baseline_gate

        baselines = {"random_guess": {"score": 10.0, "std": 0.0}}
        assert passes_baseline_gate(15.0, baselines, direction="minimize") is False


# ---------------------------------------------------------------------------
# FT baselines
# ---------------------------------------------------------------------------


class TestFTBaselines:
    """Fine-tuning baseline computation and gate."""

    def test_compute_baselines_loss(self):
        from gsd_ml.baselines.finetuning import compute_baselines

        baselines = compute_baselines(metric="loss", vocab_size=32000)
        assert "random_guess" in baselines
        assert "untrained_model" in baselines
        assert baselines["random_guess"]["score"] > baselines["untrained_model"]["score"]

    def test_compute_baselines_perplexity(self):
        from gsd_ml.baselines.finetuning import compute_baselines

        baselines = compute_baselines(metric="perplexity", vocab_size=32000)
        assert baselines["random_guess"]["score"] == 32000.0

    def test_passes_baseline_gate_minimize_passes(self):
        from gsd_ml.baselines.finetuning import passes_baseline_gate

        baselines = {"random_guess": {"score": 10.0, "std": 0.0}}
        assert passes_baseline_gate(2.0, baselines, direction="minimize") is True

    def test_passes_baseline_gate_minimize_fails(self):
        from gsd_ml.baselines.finetuning import passes_baseline_gate

        baselines = {"random_guess": {"score": 10.0, "std": 0.0}}
        assert passes_baseline_gate(15.0, baselines, direction="minimize") is False

    def test_passes_baseline_gate_maximize_passes(self):
        from gsd_ml.baselines.finetuning import passes_baseline_gate

        baselines = {"baseline": {"score": 0.3, "std": 0.0}}
        assert passes_baseline_gate(0.5, baselines, direction="maximize") is True
