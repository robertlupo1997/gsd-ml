"""Smoke test: all 17 gsd_ml modules import without error."""

from __future__ import annotations


def test_all_modules_import():
    """All 17 gsd_ml modules import cleanly."""
    from gsd_ml import state, checkpoint, profiler, guardrails, results
    from gsd_ml import journal, diagnostics, drafts, stagnation
    from gsd_ml import retrospective, export
    from gsd_ml.baselines import tabular, deeplearning, finetuning
    from gsd_ml.prepare import tabular as pt, deeplearning as pd, finetuning as pf

    # Verify key exports exist
    assert hasattr(state, "SessionState")
    assert hasattr(checkpoint, "save_checkpoint")
    assert hasattr(profiler, "profile_dataset")
    assert hasattr(guardrails, "ResourceGuardrails")
    assert hasattr(results, "ResultsTracker")
    assert hasattr(journal, "append_journal_entry")
    assert hasattr(diagnostics, "diagnose_regression")
    assert hasattr(drafts, "ALGORITHM_FAMILIES")
    assert hasattr(stagnation, "check_stagnation")
    assert hasattr(retrospective, "generate_retrospective")
    assert hasattr(export, "export_artifact")
    assert hasattr(tabular, "compute_baselines")
    assert hasattr(deeplearning, "compute_baselines")
    assert hasattr(finetuning, "compute_baselines")
    assert hasattr(pt, "load_data")
    assert hasattr(pd, "get_device_info")
    assert hasattr(pf, "get_vram_info")
