# Phase 2: Core Workflow (Tabular) - Research

**Researched:** 2026-03-22
**Domain:** Claude Code workflow orchestration + tabular ML experiment loop
**Confidence:** HIGH

## Summary

Phase 2 transforms gsd-ml from a package skeleton into a working ML research tool. The core deliverable is a workflow markdown file (`ml-run.md`) that Claude Code follows step-by-step to run a complete tabular ML experiment: profile a CSV, scaffold a `.ml/` directory, generate prepare.py and train.py, then iterate (edit train.py, run it, parse JSON metrics from stdout, keep/revert via git) until guardrails trip. Finally, export the best model and generate a retrospective.

All Python utilities needed for this phase already exist and are tested (162 tests passing): `profiler.py`, `guardrails.py`, `state.py`, `checkpoint.py`, `results.py`, `journal.py`, `retrospective.py`, `export.py`, `baselines/tabular.py`, `prepare/tabular.py`. The work is primarily: (1) write the workflow .md that instructs Claude Code how to orchestrate these utilities, (2) create the static `train-tabular.py` template (de-Jinja2'd from mlforge's `tabular_train.py.j2`), and (3) write a `config.json` schema for experiment configuration.

**Primary recommendation:** Structure the workflow as a single `ml-run.md` with clearly labeled phases (profile, scaffold, loop, finalize) that Claude Code follows sequentially. The workflow calls Python utilities via `python -c "..."` Bash commands and uses native git commands for state management.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PROF-01 | Auto-detect task type (classification vs regression) from target column | `profiler.profile_dataset()` already does this -- workflow calls it via `python -c` |
| PROF-02 | Auto-select appropriate metric based on task type | `profiler.profile_dataset()` returns metric+direction -- already implemented |
| PROF-03 | Detect data leakage and warn user | `profiler.profile_dataset()` calls `validate_no_leakage()` -- returns `leakage_warnings` |
| PROF-04 | Report dataset statistics (rows, features, missing %, types) | `DatasetProfile` dataclass has all fields -- workflow prints summary |
| SCAF-01 | Create .ml/ state directory with config, checkpoint, journal files | Workflow creates `.ml/` dir, writes `config.json`, empty `results.jsonl` |
| SCAF-02 | Generate domain-appropriate frozen prepare.py | Workflow copies `prepare/tabular.py` content into `.ml/prepare.py` |
| SCAF-03 | Generate domain-appropriate starter train.py | Static template `train-tabular.py` needs creation (de-Jinja2 from mlforge) |
| SCAF-04 | Create git branch for experiment run (ml/run-{id}) | Workflow runs `git checkout -b ml/run-{id}` |
| LOOP-01 | Claude Code edits train.py directly (no subprocess spawning) | Core workflow pattern: Claude uses Edit tool on `.ml/train.py` |
| LOOP-02 | Claude Code runs train.py via Bash and parses JSON metric from stdout | Workflow runs `cd .ml && python train.py` and parses last JSON line |
| LOOP-03 | Keep decision: git commit on improvement | Workflow uses `DeviationHandler.handle()` then `git add . && git commit` |
| LOOP-04 | Revert decision: git checkout on non-improvement | Workflow runs `git checkout -- .ml/train.py` on revert |
| LOOP-05 | Retry decision: re-run with reduced resources on OOM | `DeviationHandler` returns "retry" on OOM -- workflow edits train.py to reduce resources |
| LOOP-06 | Stop decision: halt on repeated OOM or guardrail trip | `DeviationHandler` returns "stop" after MAX_RETRIES OOMs |
| GUARD-01 | Enforce experiment count limit | `ResourceGuardrails.should_stop()` checks `budget_experiments` |
| GUARD-02 | Enforce time budget (minutes) | `ResourceGuardrails.should_stop()` checks elapsed vs `budget_minutes` |
| GUARD-03 | Enforce disk space minimum (1GB free) | `ResourceGuardrails.should_stop()` checks `shutil.disk_usage()` |
| GUARD-04 | Stop gracefully when any guardrail trips | Workflow checks guardrails before each iteration, breaks loop |
| STATE-01 | Checkpoint saves after every experiment iteration | Workflow calls `save_checkpoint()` via `python -c` after each iteration |
| STATE-03 | Append-only results.jsonl survives partial writes | `ResultsTracker.add()` appends single line -- already atomic |
| STATE-04 | Human-readable experiments.md journal updated per iteration | Workflow calls `append_journal_entry()` + `render_journal_markdown()` |
| TAB-01 | sklearn, XGBoost, LightGBM model families supported | Static train.py template includes all three with try/except imports |
| TAB-02 | Metrics: accuracy, f1, f1_weighted, r2, rmse, mae | `profiler.py` auto-selects; `evaluate()` in prepare/tabular accepts any sklearn scoring |
| TAB-03 | Cross-validation evaluation in train.py | `prepare/tabular.py evaluate()` uses StratifiedKFold/KFold -- train.py calls it |
| TAB-04 | Tabular-specific baselines (most_frequent, stratified, mean, median) | `baselines/tabular.py compute_baselines()` already implements all four |
| FIN-01 | Export best model artifact with metadata.json sidecar | `export.export_artifact()` handles joblib copy + metadata.json |
| FIN-02 | Generate retrospective markdown (what worked, what didn't, trajectory) | `retrospective.generate_retrospective()` already implemented |
| FIN-03 | Tag best commit in git (ml-best-{run_id}) | Workflow runs `git tag ml-best-{run_id} {best_commit}` |
</phase_requirements>

## Standard Stack

### Core (already ported in Phase 1)
| Module | Purpose | Status |
|--------|---------|--------|
| `gsd_ml.profiler` | Dataset profiling, task/metric auto-detection, leakage check | Ready (tested) |
| `gsd_ml.guardrails` | ResourceGuardrails, CostTracker, DeviationHandler | Ready (tested) |
| `gsd_ml.state` | SessionState dataclass | Ready (tested) |
| `gsd_ml.checkpoint` | save_checkpoint / load_checkpoint with atomic writes | Ready (tested) |
| `gsd_ml.results` | ResultsTracker with JSONL append | Ready (tested) |
| `gsd_ml.journal` | JournalEntry, append, load, render markdown | Ready (tested) |
| `gsd_ml.retrospective` | generate_retrospective markdown | Ready (tested) |
| `gsd_ml.export` | export_artifact with metadata.json sidecar | Ready (tested) |
| `gsd_ml.baselines.tabular` | compute_baselines, passes_baseline_gate | Ready (tested) |
| `gsd_ml.prepare.tabular` | load_data, split_data, build_preprocessor, evaluate | Ready (tested) |

### New Artifacts to Create
| Artifact | Purpose |
|----------|---------|
| `gsd-ml/workflows/ml-run.md` | Main workflow -- replaces mlforge's `engine.py` |
| `gsd-ml/templates/train-tabular.py` | Static starter train.py (de-Jinja2'd) |
| `gsd-ml/references/metric-map.md` | Metric name to sklearn scoring string mapping |

### Python Dependencies (for train.py runtime)
| Library | Purpose | Import Strategy |
|---------|---------|-----------------|
| scikit-learn | Core ML, preprocessing, CV | Required |
| pandas | Data loading | Required |
| numpy | Numeric ops | Required |
| joblib | Model serialization | Required (ships with sklearn) |
| xgboost | XGBoost models | Optional (try/except) |
| lightgbm | LightGBM models | Optional (try/except) |

## Architecture Patterns

### Workflow-Driven Architecture

The key architectural insight: mlforge's `engine.py` (Python class that spawns `claude -p`) becomes `ml-run.md` (workflow markdown that Claude Code follows directly). The workflow is not code -- it is structured instructions that Claude Code interprets.

```
commands/gsd-ml/ml.md          # Skill entry point (exists)
  |
  v
gsd-ml/workflows/ml-run.md    # Main workflow (TO CREATE)
  |
  +-- Phase 1: Profile         # python -c "from gsd_ml.profiler import ..."
  +-- Phase 2: Scaffold         # mkdir .ml/, write config.json, copy prepare.py, write train.py
  +-- Phase 3: Loop             # edit train.py -> bash run -> parse JSON -> keep/revert
  +-- Phase 4: Finalize         # export artifact, retrospective, git tag
```

### .ml/ Directory Structure
```
.ml/
  config.json           # Experiment configuration (task, metric, direction, budgets)
  prepare.py            # Frozen data pipeline (copied from gsd_ml.prepare.tabular)
  train.py              # Mutable training script (Claude edits this)
  results.jsonl         # Append-only experiment results
  experiments.jsonl      # Journal entries (JSONL)
  experiments.md         # Human-readable journal (rendered from JSONL)
  checkpoint.json        # Session state checkpoint
  best_model.joblib      # Best model artifact (saved by train.py)
  predictions.csv        # Latest predictions (saved by train.py)
  artifacts/             # Export directory (created at finalization)
    best_model.joblib    # Copy of best model
    metadata.json        # Metric value, commit hash, cost, timestamp
  RETROSPECTIVE.md       # Generated at end of run
```

### Pattern: Python Utility Invocation via Bash

Claude Code calls Python utilities through `python -c "..."` commands. This is the bridge pattern.

```bash
# Profile dataset
python -c "
import json, pandas as pd
from gsd_ml.profiler import profile_dataset
from dataclasses import asdict
df = pd.read_csv('dataset.csv')
profile = profile_dataset(df, 'target')
print(json.dumps(asdict(profile), default=str))
"

# Check guardrails
python -c "
import json
from gsd_ml.state import SessionState
from gsd_ml.guardrails import ResourceGuardrails
state = SessionState(**json.loads('${STATE_JSON}'))
guard = ResourceGuardrails(json.loads('${CONFIG_JSON}'), Path('.ml'))
reason = guard.stop_reason(state)
print(json.dumps({'should_stop': reason is not None, 'reason': reason}))
"

# Save checkpoint
python -c "
import json
from pathlib import Path
from gsd_ml.state import SessionState
from gsd_ml.checkpoint import save_checkpoint
state = SessionState(**json.loads('${STATE_JSON}'))
save_checkpoint(state, Path('.ml'))
"
```

### Pattern: train.py JSON Contract

train.py MUST print a single JSON line to stdout as its last output:

```python
# Success:
print(json.dumps({"metric_value": 0.847, "metric_name": "accuracy"}))

# train.py is run from .ml/ directory:
# cd .ml && python train.py
```

Claude Code captures stdout, extracts the last JSON line, and uses `metric_value` for keep/revert decisions.

### Pattern: Keep/Revert via Git

```bash
# On improvement (keep):
cd .ml && git add . && git commit -m "exp-{N}: {metric}={value} ({description})"

# On non-improvement (revert):
cd .ml && git checkout -- train.py

# Note: only train.py is reverted. results.jsonl, experiments.jsonl,
# checkpoint.json are NOT reverted (they are append-only state).
```

### Pattern: Static Template with Placeholders

The static `train-tabular.py` template uses Python string constants (not Jinja2) that Claude Code replaces via the Write tool when scaffolding:

```python
# Configuration -- set by gsd-ml scaffolder
CSV_PATH = "__CSV_PATH__"
TARGET_COLUMN = "__TARGET_COLUMN__"
METRIC = "__METRIC__"
TASK = "__TASK__"
```

Claude Code reads the template, replaces placeholders, and writes the customized version to `.ml/train.py`.

### Anti-Patterns to Avoid
- **Spawning subprocesses for the loop:** Claude Code IS the loop. No `claude -p`, no Task tools for experiment iterations.
- **Using Jinja2 for templates:** Static Python files with placeholder strings. Claude Code replaces them via Write/Edit.
- **Complex Python orchestrator scripts:** The workflow .md IS the orchestrator. Python utilities are leaf functions called individually.
- **Reverting everything on non-improvement:** Only revert `train.py`. State files (results.jsonl, checkpoint.json, experiments.jsonl) must survive reverts.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Dataset profiling | Custom CSV analysis | `gsd_ml.profiler.profile_dataset()` | Handles edge cases (empty data, all-NaN, leakage detection) |
| Data preprocessing | Custom imputer/scaler | `gsd_ml.prepare.tabular.build_preprocessor()` | Handles mixed types, missing values, one-hot encoding |
| Cross-validation | Manual train/test splits | `gsd_ml.prepare.tabular.evaluate()` | Stratified for classification, proper KFold |
| Baseline computation | Hardcoded thresholds | `gsd_ml.baselines.tabular.compute_baselines()` | Proper CV'd dummy models |
| Keep/revert logic | Custom comparison | `gsd_ml.guardrails.DeviationHandler.handle()` | Handles OOM, timeout, NaN, direction |
| Checkpoint persistence | Custom file I/O | `gsd_ml.checkpoint.save_checkpoint()` | Atomic write-then-rename, schema versioned |
| Results tracking | Custom log parsing | `gsd_ml.results.ResultsTracker` | JSONL append-only, queryable, summary stats |
| Artifact export | Custom copy logic | `gsd_ml.export.export_artifact()` | Handles joblib/pt/adapter, metadata sidecar |

**Key insight:** Every Python utility is already ported and tested. The workflow only needs to orchestrate them.

## Common Pitfalls

### Pitfall 1: Reverting State Files Along with train.py
**What goes wrong:** `git checkout -- .` reverts results.jsonl and checkpoint.json, losing experiment history.
**Why it happens:** Instinct to revert all changes on non-improvement.
**How to avoid:** Only revert train.py: `git checkout -- train.py`. State files are append-only and must survive.
**Warning signs:** Experiment count resets, results.jsonl shrinks after revert.

### Pitfall 2: JSON Parsing from stdout Noise
**What goes wrong:** train.py prints warnings, progress bars, or other text. JSON parsing fails.
**Why it happens:** Libraries like sklearn, xgboost print to stdout.
**How to avoid:** Parse the LAST line of stdout that looks like valid JSON. Or redirect stderr: `python train.py 2>/dev/null`. Or use `python -u train.py 2>.ml/train.log` and parse only the final line.
**Warning signs:** JSONDecodeError, metric_value always None.

### Pitfall 3: Working Directory Confusion
**What goes wrong:** train.py can't find dataset or prepare.py because CWD is wrong.
**Why it happens:** Claude Code runs bash from project root, not from .ml/.
**How to avoid:** Always `cd .ml && python train.py`. train.py uses relative paths from .ml/.
**Warning signs:** FileNotFoundError for CSV or prepare.py.

### Pitfall 4: Git Branch Not Created Before First Commit
**What goes wrong:** Experiment commits land on main branch.
**Why it happens:** Scaffolding step forgets to create branch.
**How to avoid:** Workflow must create `ml/run-{id}` branch before the loop starts.
**Warning signs:** Commits appearing on main, no experiment branch visible.

### Pitfall 5: Guardrail Timing in the Workflow
**What goes wrong:** Guardrail check uses a ResourceGuardrails Python object that doesn't persist across `python -c` calls, so `_start_time` resets.
**Why it happens:** Each `python -c` call creates a new ResourceGuardrails instance.
**How to avoid:** Store `start_time` in config.json or checkpoint.json. Or use the simpler approach: track experiment count and elapsed time in the workflow itself (Claude reads the clock, counts iterations).
**Warning signs:** Time budget never trips, experiment count off.

### Pitfall 6: prepare.py Frozen but Needs Dataset Path
**What goes wrong:** prepare.py has `load_data(path)` but the path varies per dataset.
**Why it happens:** prepare.py is "frozen" (agent must not edit it) but needs the CSV path.
**How to avoid:** train.py receives the CSV path via constant and passes it to prepare functions. prepare.py is a library, not a standalone script.
**Warning signs:** Hardcoded paths in prepare.py.

## Code Examples

### Workflow Config JSON Schema
```json
{
  "run_id": "run-20260322-143000",
  "domain": "tabular",
  "dataset_path": "../dataset.csv",
  "target_column": "target",
  "task": "classification",
  "metric": "accuracy",
  "direction": "maximize",
  "budget_experiments": 25,
  "budget_minutes": 60,
  "budget_usd": 5.0,
  "start_time": "2026-03-22T14:30:00Z"
}
```

### Static train-tabular.py Template (de-Jinja2'd)
```python
"""Mutable train.py -- Claude Code edits this file each iteration.

This is the ONLY file Claude may modify. prepare.py is frozen.
Outputs JSON to stdout: {"metric_value": <float>, "metric_name": "<name>"}
"""
import json
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Import frozen data pipeline
from prepare import load_data, split_data, build_preprocessor, evaluate

# --- Configuration (set by gsd-ml scaffolder) ---
CSV_PATH = "__CSV_PATH__"
TARGET_COLUMN = "__TARGET_COLUMN__"
METRIC = "__METRIC__"
TASK = "__TASK__"

# Optional imports (Claude may add these)
try:
    import xgboost as xgb
except ImportError:
    xgb = None
try:
    import lightgbm as lgb
except ImportError:
    lgb = None

def main():
    # Load and split
    df = load_data(Path(CSV_PATH))
    X_train, X_test, y_train, y_test = split_data(df, TARGET_COLUMN)

    # Preprocess
    preprocessor = build_preprocessor(X_train)
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)

    # Model
    model = RandomForestClassifier(n_estimators=100, random_state=42)

    # Evaluate with cross-validation
    result = evaluate(model, X_train_proc, y_train, scoring=METRIC, task=TASK)

    # Retrain on full train set and save
    model.fit(X_train_proc, y_train)
    preds = model.predict(X_test_proc)
    pd.DataFrame({"y_true": y_test, "y_pred": preds}).to_csv("predictions.csv", index=False)
    joblib.dump(model, "best_model.joblib")

    # Output metric as JSON
    print(json.dumps({"metric_value": result["mean"], "metric_name": METRIC}))

if __name__ == "__main__":
    main()
```

### Workflow Guardrail Check Pattern

Since ResourceGuardrails doesn't persist across python -c calls, the workflow should track guardrails directly:

```markdown
## Guardrail Check (before each iteration)

1. Read `.ml/config.json` to get budgets
2. Read `.ml/checkpoint.json` to get current state
3. Check: `experiment_count >= budget_experiments` -> STOP
4. Check: elapsed time (now - start_time) >= budget_minutes * 60 -> STOP
5. Run: `python -c "import shutil; u=shutil.disk_usage('.'); print(u.free/(1024**3))"` -> if < 1.0 -> STOP
6. If none tripped -> continue loop
```

This avoids the stale `_start_time` problem by reading `start_time` from config.json.

## State of the Art

| Old Approach (mlforge) | New Approach (gsd-ml) | Impact |
|------------------------|----------------------|--------|
| Python `engine.py` spawns `claude -p` | Workflow .md instructs Claude Code directly | No double billing, full context continuity |
| Jinja2 templates (`*.j2`) | Static Python files with placeholder strings | No Jinja2 dependency, simpler |
| GitPython for git ops | `subprocess.run(["git", ...])` or Bash tool | No GitPython dependency |
| TOML config via `tomllib` | JSON config via `json` module | Native JS/Python interop |
| `Config` dataclass | Plain dict from JSON | Simpler, Claude can read/write directly |

## Open Questions

1. **Cost tracking without API access**
   - What we know: mlforge tracked `claude -p` costs via `--output-format json`. In gsd-ml, Claude Code IS the agent -- there's no subprocess cost to track.
   - What's unclear: Should we track Claude Code's own API cost? We likely can't from inside the session.
   - Recommendation: Set `cost_spent_usd` to 0 or estimate from experiment count. The `budget_usd` guardrail becomes effectively disabled for v1. Experiment count and time budget are the real guardrails.

2. **Workflow length and context**
   - What we know: The workflow .md will be long (profile + scaffold + loop + finalize).
   - What's unclear: Will Claude Code follow a very long workflow reliably?
   - Recommendation: Keep each section self-contained with clear step numbering. Use `<step>` XML tags like GSD does. The skill file already loads the workflow via `@~/.claude/gsd-ml/workflows/ml-run.md`.

3. **Selective git revert strategy**
   - What we know: Only train.py should be reverted. State files must survive.
   - What's unclear: Should we use `.gitignore` for state files, or rely on selective `git checkout -- train.py`?
   - Recommendation: Do NOT gitignore state files -- they should be committed with keeps. Use selective revert: `git checkout -- train.py` only. Add state files to commits so the journal is preserved in git history.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | `python/pyproject.toml` (pytest section) |
| Quick run command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` |
| Full suite command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROF-01 | Auto-detect classification vs regression | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes |
| PROF-02 | Auto-select metric | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes |
| PROF-03 | Detect data leakage | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes |
| PROF-04 | Report dataset stats | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes |
| SCAF-01 | Create .ml/ directory structure | integration | Manual -- verify .ml/ dir created by workflow | N/A (workflow) |
| SCAF-02 | Generate frozen prepare.py | integration | Manual -- verify prepare.py content matches module | N/A (workflow) |
| SCAF-03 | Generate starter train.py | smoke | `python -c "exec(open('gsd-ml/templates/train-tabular.py').read())"` -- syntax check | Wave 0 |
| SCAF-04 | Create git branch | integration | Manual -- verify branch exists after workflow | N/A (workflow) |
| LOOP-01-06 | Edit/run/parse/keep/revert/retry/stop | integration | End-to-end workflow test (manual) | N/A (workflow) |
| GUARD-01 | Experiment count limit | unit | `python -m pytest python/tests/test_guardrails.py -x -q` | Yes |
| GUARD-02 | Time budget | unit | `python -m pytest python/tests/test_guardrails.py -x -q` | Yes |
| GUARD-03 | Disk space check | unit | `python -m pytest python/tests/test_guardrails.py -x -q` | Yes |
| GUARD-04 | Graceful stop | unit | `python -m pytest python/tests/test_guardrails.py -x -q` | Yes |
| STATE-01 | Checkpoint saves | unit | `python -m pytest python/tests/test_checkpoint.py -x -q` | Yes |
| STATE-03 | Append-only results.jsonl | unit | `python -m pytest python/tests/test_results.py -x -q` | Yes |
| STATE-04 | experiments.md journal | unit | `python -m pytest python/tests/test_journal.py -x -q` | Yes |
| TAB-01 | sklearn/XGBoost/LightGBM support | smoke | Template syntax + import check | Wave 0 |
| TAB-02 | Metric names supported | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes |
| TAB-03 | Cross-validation evaluation | unit | `python -m pytest python/tests/test_baselines.py -x -q` | Yes |
| TAB-04 | Tabular baselines | unit | `python -m pytest python/tests/test_baselines.py -x -q` | Yes |
| FIN-01 | Export best model | unit | `python -m pytest python/tests/test_export.py -x -q` | Yes |
| FIN-02 | Generate retrospective | unit | `python -m pytest python/tests/test_retrospective.py -x -q` | Yes |
| FIN-03 | Tag best commit | integration | Manual -- verify git tag exists | N/A (workflow) |

### Sampling Rate
- **Per task commit:** `python -m pytest python/tests/ -x -q` (existing tests must stay green)
- **Per wave merge:** Full suite + manual smoke test of workflow with sample CSV
- **Phase gate:** Full suite green + end-to-end run of `/gsd:ml` on a test CSV

### Wave 0 Gaps
- [ ] `gsd-ml/templates/train-tabular.py` -- static template needs creation and syntax validation
- [ ] End-to-end smoke test with a small CSV (iris-style) -- manual verification that workflow produces .ml/ with expected files

## Sources

### Primary (HIGH confidence)
- Existing codebase: all Python modules in `python/src/gsd_ml/` -- read and verified
- mlforge source at `/home/tlupo/AutoML/src/mlforge/` -- engine.py, config.py, templates reviewed
- GSD pattern: `~/.claude/get-shit-done/workflows/` -- workflow structure verified

### Secondary (MEDIUM confidence)
- GSD skill pattern: `commands/gsd-ml/ml.md` and `gsd-ml/workflows/ml-run.md` -- stub exists, pattern clear

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all Python modules already ported and tested
- Architecture: HIGH -- follows mlforge's proven pattern, adapted for Claude Code native execution
- Pitfalls: HIGH -- derived from mlforge production experience (609 tests, 3 domains)

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- no external dependency changes expected)
