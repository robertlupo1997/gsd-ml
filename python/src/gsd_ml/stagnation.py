"""Branch-on-stagnation logic for escaping local optima.

When the agent hits N consecutive reverts, it branches from the best-ever
commit and tries a different model family.
"""

from __future__ import annotations

import subprocess

from gsd_ml.state import SessionState


def check_stagnation(state: SessionState, threshold: int = 3) -> bool:
    """Check whether the session has stagnated.

    Args:
        state: Current session state.
        threshold: Number of consecutive reverts that signals stagnation.

    Returns:
        True if consecutive_reverts >= threshold.
    """
    return state.consecutive_reverts >= threshold


def trigger_stagnation_branch(
    repo_path: str,
    state: SessionState,
    new_family: str,
) -> str | None:
    """Create an exploration branch from the best-ever commit.

    Args:
        repo_path: Path to the git repository.
        state: Current session state (must have best_commit set).
        new_family: Algorithm family name for the new branch.

    Returns:
        The branch name created (``explore-{new_family}``), or None if
        best_commit is not set.
    """
    if state.best_commit is None:
        return None

    # Checkout the best-ever commit (detached HEAD)
    subprocess.run(
        ["git", "checkout", state.best_commit],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )

    # Create and checkout the exploration branch
    branch_name = f"explore-{new_family}"
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=repo_path,
        capture_output=True,
        check=True,
    )

    # Reset stagnation counter
    state.consecutive_reverts = 0

    return branch_name
