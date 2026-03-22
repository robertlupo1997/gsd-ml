"""Shared fixtures for gsd_ml tests."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _reset_gsd_ml_logger():
    """Clear gsd_ml logger handlers between tests to prevent leakage."""
    yield
    gsd_ml_logger = logging.getLogger("gsd_ml")
    gsd_ml_logger.handlers.clear()


@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for test file operations."""
    return tmp_path


@pytest.fixture
def sample_config() -> dict:
    """Return a valid config dict for testing."""
    return {
        "domain": "tabular",
        "metric": "rmse",
        "direction": "minimize",
        "budget_minutes": 120,
        "budget_experiments": 100,
        "budget_usd": 5.0,
    }


@pytest.fixture
def sample_state():
    """Return a populated SessionState for testing."""
    from gsd_ml.state import SessionState

    return SessionState(
        experiment_count=5,
        best_metric=0.95,
        best_commit="abc1234",
        budget_remaining=45.0,
        consecutive_reverts=1,
        total_keeps=3,
        total_reverts=2,
        run_id="test-run-001",
    )
