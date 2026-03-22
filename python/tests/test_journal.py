"""Tests for gsd_ml.journal -- experiment journal with diff-aware entries."""

from __future__ import annotations

import subprocess
from pathlib import Path

from gsd_ml.journal import (
    JournalEntry,
    append_journal_entry,
    get_last_diff,
    load_journal,
    render_journal_markdown,
)


class TestJournalEntryDiffField:
    """JournalEntry supports optional diff field."""

    def test_journal_entry_diff_field_default(self):
        entry = JournalEntry(
            experiment_id=1,
            hypothesis="test",
            result="ok",
            metric_value=0.9,
            metric_delta=None,
            commit_hash="abc1234",
            status="keep",
        )
        assert entry.diff is None

    def test_journal_entry_with_diff(self):
        from dataclasses import asdict

        entry = JournalEntry(
            experiment_id=2,
            hypothesis="add feature",
            result="improved",
            metric_value=0.95,
            metric_delta=0.05,
            commit_hash="def5678",
            status="keep",
            diff="--- a/train.py\n+++ b/train.py\n@@ -1 +1 @@\n-old\n+new",
        )
        d = asdict(entry)
        assert d["diff"] == "--- a/train.py\n+++ b/train.py\n@@ -1 +1 @@\n-old\n+new"


class TestJournalDiffRoundTrip:
    """Diff field persists through JSONL serialization."""

    def test_append_and_load_with_diff(self, tmp_dir: Path):
        journal_path = tmp_dir / "experiments.jsonl"
        diff_text = "--- a/train.py\n+++ b/train.py\n@@ changed @@"

        entry = JournalEntry(
            experiment_id=1,
            hypothesis="test diff",
            result="ok",
            metric_value=0.9,
            metric_delta=None,
            commit_hash="abc1234",
            status="keep",
            diff=diff_text,
        )
        append_journal_entry(journal_path, entry)
        loaded = load_journal(journal_path)

        assert len(loaded) == 1
        assert loaded[0]["diff"] == diff_text

    def test_append_and_load_without_diff(self, tmp_dir: Path):
        journal_path = tmp_dir / "experiments.jsonl"

        entry = JournalEntry(
            experiment_id=1,
            hypothesis="no diff",
            result="ok",
            metric_value=0.8,
            metric_delta=None,
            commit_hash=None,
            status="revert",
        )
        append_journal_entry(journal_path, entry)
        loaded = load_journal(journal_path)

        assert len(loaded) == 1
        assert loaded[0]["diff"] is None


class TestRenderMarkdownWithDiff:
    """Markdown rendering includes diff information when present."""

    def test_render_markdown_with_diff(self):
        long_diff = "x" * 600
        entries = [
            {
                "experiment_id": 1,
                "status": "keep",
                "metric_value": 0.9,
                "metric_delta": None,
                "hypothesis": "test",
                "commit_hash": "abc1234",
                "diff": long_diff,
            }
        ]
        md = render_journal_markdown(entries)
        assert "x" * 500 in md
        assert "x" * 600 not in md
        assert "..." in md

    def test_render_markdown_without_diff(self):
        entries = [
            {
                "experiment_id": 1,
                "status": "keep",
                "metric_value": 0.9,
                "metric_delta": None,
                "hypothesis": "test",
                "commit_hash": "abc1234",
            }
        ]
        md = render_journal_markdown(entries)
        assert "| 1 |" in md
        assert "Diff" not in md.lower() or "diff" not in md.split("|")[0]


class TestGetLastDiff:
    """get_last_diff retrieves git diff from repository."""

    def test_get_last_diff_with_commits(self, tmp_dir: Path):
        """Returns diff string from a git repo with multiple commits."""
        subprocess.run(["git", "init"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_dir, capture_output=True, check=True)
        # First commit
        f = tmp_dir / "train.py"
        f.write_text("print('v1')\n")
        subprocess.run(["git", "add", "train.py"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_dir, capture_output=True, check=True)
        # Second commit
        f.write_text("print('v2')\n")
        subprocess.run(["git", "add", "train.py"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "update"], cwd=tmp_dir, capture_output=True, check=True)

        diff = get_last_diff(tmp_dir)
        assert diff is not None
        assert "train.py" in diff
        assert "v1" in diff or "v2" in diff

    def test_get_last_diff_no_previous(self, tmp_dir: Path):
        """Returns None when only one commit exists."""
        subprocess.run(["git", "init"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_dir, capture_output=True, check=True)
        f = tmp_dir / "train.py"
        f.write_text("print('v1')\n")
        subprocess.run(["git", "add", "train.py"], cwd=tmp_dir, capture_output=True, check=True)
        subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_dir, capture_output=True, check=True)

        diff = get_last_diff(tmp_dir)
        assert diff is None
