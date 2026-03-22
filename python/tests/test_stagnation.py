"""Tests for stagnation detection and branch-on-stagnation."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from gsd_ml.stagnation import check_stagnation, trigger_stagnation_branch
from gsd_ml.state import SessionState


@pytest.fixture
def git_repo(tmp_path: Path) -> Path:
    """Create a temporary git repo with an initial commit. Returns repo path."""
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True, check=True)
    readme = tmp_path / "README.md"
    readme.write_text("init")
    subprocess.run(["git", "add", "README.md"], cwd=tmp_path, capture_output=True, check=True)
    subprocess.run(["git", "commit", "-m", "initial commit"], cwd=tmp_path, capture_output=True, check=True)
    return tmp_path


class TestCheckStagnation:
    def test_below_threshold(self):
        state = SessionState(consecutive_reverts=2)
        assert check_stagnation(state) is False

    def test_at_threshold(self):
        state = SessionState(consecutive_reverts=3)
        assert check_stagnation(state) is True

    def test_above_threshold(self):
        state = SessionState(consecutive_reverts=5)
        assert check_stagnation(state) is True

    def test_custom_threshold(self):
        state = SessionState(consecutive_reverts=2)
        assert check_stagnation(state, threshold=2) is True
        assert check_stagnation(state, threshold=3) is False


class TestTriggerStagnationBranch:
    def test_creates_branch(self, git_repo: Path):
        best_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        state = SessionState(
            consecutive_reverts=3,
            best_commit=best_commit,
        )
        branch_name = trigger_stagnation_branch(str(git_repo), state, "xgboost")
        assert branch_name == "explore-xgboost"
        active_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=git_repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        assert active_branch == "explore-xgboost"

    def test_resets_counter(self, git_repo: Path):
        best_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=git_repo, capture_output=True, text=True, check=True
        ).stdout.strip()
        state = SessionState(
            consecutive_reverts=5,
            best_commit=best_commit,
        )
        trigger_stagnation_branch(str(git_repo), state, "lightgbm")
        assert state.consecutive_reverts == 0

    def test_no_best_commit_returns_none(self, git_repo: Path):
        state = SessionState(consecutive_reverts=3, best_commit=None)
        result = trigger_stagnation_branch(str(git_repo), state, "svm")
        assert result is None
        assert state.consecutive_reverts == 3
