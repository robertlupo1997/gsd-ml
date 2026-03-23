---
phase: 02-core-workflow-tabular
verified: 2026-03-23T00:10:00Z
status: passed
score: 7/7 truths verified
re_verification:
  previous_status: gaps_found
  previous_score: 3/7
  gaps_closed:
    - "Claude Code iterates: edit train.py -> run -> parse metric -> keep/revert"
    - "Guardrails stop the loop when budget exhausted"
    - "Best model exported to .ml/artifacts/ with metadata"
    - "Retrospective markdown generated"
    - "Workflow saves checkpoint and appends results after every iteration"
    - "Workflow creates .ml/ directory with prepare.py, train.py, config.json"
  gaps_remaining: []
  regressions: []
---

# Phase 2: Core Workflow Tabular Verification Report

**Phase Goal:** `/gsd:ml dataset.csv target` runs a complete tabular ML experiment end-to-end
**Verified:** 2026-03-23
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 02-03 fixed all 6 broken Python bridge calls)

---

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|---------|
| 1 | Claude Code profiles a CSV and auto-detects classification vs regression | VERIFIED | ml-run.md Step 1.3 calls `profile_dataset(df, '{target_column}')` with correct positional args; profiler.py exists at python/src/gsd_ml/profiler.py; DatasetProfile fields task/metric/direction/leakage_warnings all referenced correctly in Steps 1.4-1.6 |
| 2 | `.ml/` directory scaffolded with prepare.py, train.py, config.json | VERIFIED | Steps 2.2-2.9 create directory, write config.json, freeze prepare.py via inspect.getsource, copy train-tabular.py template with 4 placeholder replacements. compute_baselines now calls `(X_proc, y_train, '{metric}', '{task}')` — correct arg order (scoring before task) |
| 3 | Claude Code iterates: edit train.py -> run -> parse metric -> keep/revert | VERIFIED | DeviationHandler constructed as `DeviationHandler(direction='{direction}')` and called as `handler.handle(result, state)` with result dict containing `status`/`metric_value` keys and a proper SessionState object. Keep path commits, revert path does `git checkout -- train.py` |
| 4 | Git branch created, commits on keep, reverts on non-improvement | VERIFIED | Step 2.8 `git checkout -b ml/run-{run_id}`; keep path does `git add . && git commit -m "exp-{N}: ..."` and stores commit hash; revert path does `git checkout -- train.py` only (state files preserved) |
| 5 | Guardrails stop the loop when budget exhausted | VERIFIED | Steps 3.1.1-3.1.3 check experiment count vs budget_experiments, elapsed time vs budget_minutes, and disk space via shutil. DeviationHandler's stop/retry decisions now reachable through correct `handle(result, state)` invocation |
| 6 | Best model exported to .ml/artifacts/ with metadata | VERIFIED | Step 4.1 calls `export_artifact(Path('.ml'), state, config)` — matches actual signature `export_artifact(experiment_dir: Path, state: SessionState, config: dict)`. SessionState constructed with `total_keeps`/`total_reverts` field names |
| 7 | Retrospective markdown generated | VERIFIED | Step 4.2 constructs `ResultsTracker(Path('.ml/results.jsonl'))`, builds SessionState, then calls `generate_retrospective(tracker, state, config)` — matches actual 3-arg signature. Output written to `.ml/RETROSPECTIVE.md` |

**Score:** 7/7 truths verified

---

## Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `gsd-ml/workflows/ml-run.md` | Complete experiment orchestration workflow | VERIFIED | 515 lines; all 6 Python bridge calls corrected; called by commands/gsd-ml/ml.md via @~/.claude/gsd-ml/workflows/ml-run.md |
| `gsd-ml/templates/train-tabular.py` | Static starter train.py for tabular ML | VERIFIED | 101 lines; valid Python; has all 4 placeholder constants (__CSV_PATH__, __TARGET_COLUMN__, __METRIC__, __TASK__); JSON stdout output on last print |
| `gsd-ml/references/metric-map.md` | Metric name to sklearn scoring string mapping | VERIFIED | 30 lines; all 6 metrics (accuracy, f1, f1_weighted, r2, rmse, mae) with direction; referenced in commands/gsd-ml/ml.md |
| `commands/gsd-ml/ml.md` | Skill entry point with argument parsing | VERIFIED | 10 lines; references ml-run.md workflow; parses dataset/target from $ARGUMENTS |

---

## Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.profiler` | `from gsd_ml.profiler import profile_dataset` | WIRED | Line 33; `profile_dataset(df, target_column)` matches actual signature |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.baselines.tabular` | `from gsd_ml.baselines.tabular import compute_baselines` | WIRED | Line 164: `compute_baselines(X_proc, y_train, '{metric}', '{task}')` — scoring (arg3) before task (arg4) matches actual signature |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.guardrails.DeviationHandler` | `python -c bridge call` | WIRED | Line 275: `DeviationHandler(direction='{direction}')` and line 276: `handler.handle(result, state)` — both match actual signatures |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.results.ExperimentResult` | `python -c bridge call` | WIRED | Lines 328-336: `tracker.add(ExperimentResult(experiment_id=, commit_hash=, metric_name=, metric_value=, status=, description=, timestamp=))` — all 7 fields match dataclass |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.journal.append_journal_entry` | `python -c bridge call` | WIRED | Line 356: `append_journal_entry(Path('.ml/experiments.jsonl'), entry)` — path first, entry second, matches actual signature |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.export.export_artifact` | `python -c bridge call` | WIRED | Line 416: `export_artifact(Path('.ml'), state, config)` — matches actual signature `(experiment_dir, state, config)` |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.retrospective.generate_retrospective` | `python -c bridge call` | WIRED | Line 450: `generate_retrospective(tracker, state, config)` — matches actual 3-arg signature |
| `gsd-ml/workflows/ml-run.md` | `gsd_ml.checkpoint.save_checkpoint` | `python -c bridge call` | WIRED | Line 379: `save_checkpoint(state, Path('.ml'))` — matches actual signature `(state: SessionState, checkpoint_dir: Path)` |
| `gsd-ml/workflows/ml-run.md` | git branch and commit | `git checkout -b ml/run` | WIRED | Line 174: `git checkout -b ml/run-{run_id}`; commit/revert/tag patterns all present |
| `commands/gsd-ml/ml.md` | `gsd-ml/workflows/ml-run.md` | `@~/.claude/gsd-ml/workflows/ml-run.md` | WIRED | ml.md execution_context references the workflow |

---

## Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|-------------|------------|-------------|--------|---------|
| PROF-01 | 02-02-PLAN | Auto-detect task type from target column | SATISFIED | profiler.profile_dataset correctly called; task field in DatasetProfile |
| PROF-02 | 02-01-PLAN | Auto-select metric based on task type | SATISFIED | profiler returns metric field; metric-map.md documents all 6 metric mappings |
| PROF-03 | 02-02-PLAN | Detect data leakage and warn user | SATISFIED | Step 1.6 handles leakage_warnings, asks user to continue |
| PROF-04 | 02-02-PLAN | Report dataset statistics | SATISFIED | Step 1.5 displays n_rows, n_features, missing_pct, metric, task |
| SCAF-01 | 02-02-PLAN | Create .ml/ state directory | SATISFIED | Step 2.2 mkdir -p .ml/artifacts; Step 2.6 touch results.jsonl/experiments.jsonl |
| SCAF-02 | 02-02-PLAN | Generate frozen prepare.py | SATISFIED | Step 2.4 uses inspect.getsource(tabular); NEVER edit prepare.py rule enforced |
| SCAF-03 | 02-01-PLAN | Generate starter train.py | SATISFIED | train-tabular.py template (101 lines, valid Python, 4 placeholders, JSON output) |
| SCAF-04 | 02-02-PLAN | Create git branch ml/run-{id} | SATISFIED | Step 2.8 git checkout -b ml/run-{run_id} |
| LOOP-01 | 02-02-PLAN | Claude Code edits train.py directly | SATISFIED | Step 3.2 instructs Read/Edit pattern; no subprocess spawning |
| LOOP-02 | 02-02-PLAN | Claude Code runs train.py via Bash, parses JSON metric | SATISFIED | Step 3.3: cd .ml && python train.py 2>.ml/train.log; parses last JSON line from stdout |
| LOOP-03 | 02-02-PLAN | Keep decision: git commit on improvement | SATISFIED | Step 3.4 keep path: git add . && git commit; DeviationHandler now correctly routes to keep when metric improves |
| LOOP-04 | 02-02-PLAN | Revert decision: git checkout on non-improvement | SATISFIED | Step 3.4 revert path: git checkout -- train.py only; state files preserved |
| LOOP-05 | 02-02-PLAN | Retry decision: re-run with reduced resources on OOM | SATISFIED | Step 3.4 retry path: edit train.py to reduce resources, go back to Step 3.3; DeviationHandler returns retry on OOM |
| LOOP-06 | 02-02-PLAN | Stop decision: halt on repeated OOM | SATISFIED | Step 3.4 stop path: print reason, break loop; DeviationHandler returns stop after MAX_RETRIES=2 |
| GUARD-01 | 02-02-PLAN | Enforce experiment count limit | SATISFIED | Step 3.1.1 reads budget_experiments from config.json and checks experiment_count |
| GUARD-02 | 02-02-PLAN | Enforce time budget | SATISFIED | Step 3.1.2 reads start_time from config.json, computes elapsed |
| GUARD-03 | 02-02-PLAN | Enforce disk space minimum | SATISFIED | Step 3.1.3 uses shutil.disk_usage, stops if < 1.0 GB free |
| GUARD-04 | 02-02-PLAN | Stop gracefully when guardrail trips | SATISFIED | Each guardrail check breaks loop and prints reason message |
| STATE-01 | 02-02-PLAN | Checkpoint saves after every iteration | SATISFIED | Step 3.5: save_checkpoint(state, Path('.ml')) with correct SessionState field names (total_keeps, total_reverts) |
| STATE-03 | 02-02-PLAN | Append-only results.jsonl survives partial writes | SATISFIED | Step 3.5: ResultsTracker.add(ExperimentResult(...)) with all 7 required fields; JSONL append-only design |
| STATE-04 | 02-02-PLAN | Human-readable experiments.md updated per iteration | SATISFIED | Step 3.5: JournalEntry uses correct fields (experiment_id, hypothesis, result, metric_value, metric_delta, commit_hash, status); append_journal_entry(Path, entry); render_journal_markdown writes experiments.md |
| TAB-01 | 02-01-PLAN | sklearn, XGBoost, LightGBM model families supported | SATISFIED | train-tabular.py has try/except imports for xgboost and lightgbm |
| TAB-02 | 02-01-PLAN | Metrics: accuracy, f1, f1_weighted, r2, rmse, mae | SATISFIED | metric-map.md covers all 6; profiler.py selects from them |
| TAB-03 | 02-01-PLAN | Cross-validation evaluation in train.py | SATISFIED | train-tabular.py calls evaluate(model, X_train_proc, y_train, scoring=METRIC, task=TASK) |
| TAB-04 | 02-02-PLAN | Tabular-specific baselines | SATISFIED | Step 2.7: compute_baselines(X_proc, y_train, '{metric}', '{task}') with correct arg order; baselines.tabular provides most_frequent/stratified/mean/median strategies |
| FIN-01 | 02-02-PLAN | Export best model artifact with metadata.json sidecar | SATISFIED | Step 4.1: export_artifact(Path('.ml'), state, config) — finds best_model.joblib, copies to artifacts/, writes metadata.json with metric_name/metric_value/best_commit/timestamp |
| FIN-02 | 02-02-PLAN | Generate retrospective markdown | SATISFIED | Step 4.2: generate_retrospective(tracker, state, config) with correct 3-arg signature; writes to .ml/RETROSPECTIVE.md |
| FIN-03 | 02-02-PLAN | Tag best commit in git | SATISFIED | Step 4.3: git tag ml-best-{run_id} {best_commit} |

**Requirements summary:** 27/27 SATISFIED (STATE-02 is Phase 5, not claimed by Phase 2)

**Orphaned requirements check:** STATE-02 (Resume from checkpoint) maps to Phase 5 in REQUIREMENTS.md traceability table. No Phase 2 plan claims it. Not orphaned — correctly deferred.

---

## Anti-Patterns Found

None. All 6 previously identified BLOCKER patterns have been resolved:

| Old Pattern | Was | Now | Status |
|-------------|-----|-----|--------|
| DeviationHandler construction | `DeviationHandler({})` | `DeviationHandler(direction='{direction}')` | FIXED |
| DeviationHandler.handle() call | `handle(metric_value=..., best_metric=..., direction=..., stderr=...)` | `handle(result, state)` | FIXED |
| ResultsTracker.add() | `tracker.add({dict})` | `tracker.add(ExperimentResult(...))` | FIXED |
| JournalEntry fields | Wrong field names (experiment=, kept=, model_family=) | Correct fields (experiment_id, hypothesis, result, status) | FIXED |
| append_journal_entry arg order | `(entry, path)` swapped | `(Path(...), entry)` correct | FIXED |
| export_artifact signature | `(Path(model), Path(artifacts), dict)` | `(Path('.ml'), state, config)` | FIXED |
| generate_retrospective arg count | `generate_retrospective(config)` — 1 arg | `generate_retrospective(tracker, state, config)` — 3 args | FIXED |
| compute_baselines arg order | `(X, y, '{task}', '{metric}')` swapped | `(X, y, '{metric}', '{task}')` correct | FIXED |
| SessionState field names | `keep_count=`, `revert_count=` | `total_keeps=`, `total_reverts=` | FIXED |

---

## Human Verification Required

None — all correctness criteria are verifiable programmatically via signature inspection against Python source files.

---

## Gaps Summary

No gaps. All 7 success criteria are verified. All 27 phase-2 requirements are satisfied. The root cause of the previous failure (ml-run.md written against incorrect mlforge API signatures rather than the actual ported gsd_ml signatures) has been fully resolved by plan 02-03.

**What was fixed in plan 02-03:**
- 6 python -c bridge calls in ml-run.md were rewritten to match actual gsd_ml API signatures
- DeviationHandler now correctly receives direction string (not dict) and calls handle(result_dict, SessionState)
- ResultsTracker.add() now receives ExperimentResult dataclass with all 7 required fields
- JournalEntry now uses correct field names; append_journal_entry receives (path, entry) in correct order
- export_artifact now receives (experiment_dir, state, config) in correct order
- generate_retrospective now receives all 3 required arguments (tracker, state, config)
- SessionState now constructed with total_keeps/total_reverts (not keep_count/revert_count)
- compute_baselines now called with scoring before task (arg order corrected)

---

_Verified: 2026-03-23_
_Verifier: Claude (gsd-verifier)_
