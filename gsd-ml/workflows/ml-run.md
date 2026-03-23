# ML Run Workflow
> Orchestrates a complete ML experiment: profile, scaffold, loop, finalize.
> Called by /gsd:ml skill. Do not run directly.

---

## Phase 1: Profile Dataset

**Goal:** Understand the dataset before building anything.

### Step 1.1: Parse Arguments

Extract from the skill invocation:
- `dataset_path` -- path to the CSV file (first argument)
- `target_column` -- name of the target column (second argument)
- `domain` -- defaults to `"tabular"`

### Step 1.2: Verify Dataset Exists

```bash
test -f {dataset_path} || echo "ERROR: Dataset not found at {dataset_path}"
```

If the file does not exist, STOP and report the error. Do not proceed.

### Step 1.3: Profile the Dataset

Run the profiler to auto-detect task type, metric, and dataset statistics:

```bash
python -c "
import json, pandas as pd
from gsd_ml.profiler import profile_dataset
from dataclasses import asdict
df = pd.read_csv('{dataset_path}')
profile = profile_dataset(df, '{target_column}')
print(json.dumps(asdict(profile), default=str))
"
```

### Step 1.4: Parse Profile Output

Extract from the JSON output:
- `task` -- "classification" or "regression"
- `metric` -- e.g. "accuracy", "f1", "f1_weighted", "r2", "rmse", "mae"
- `direction` -- "maximize" or "minimize"
- `n_rows` -- number of rows
- `n_features` -- number of features
- `missing_pct` -- percentage of missing values
- `leakage_warnings` -- list of leakage warnings (may be empty)

### Step 1.5: Display Profile Summary

Print a summary for the user:

```
Dataset Profile:
  Rows: {n_rows}
  Features: {n_features}
  Task: {task}
  Metric: {metric} ({direction})
  Missing: {missing_pct}%
  Leakage warnings: {len(leakage_warnings)}
```

### Step 1.6: Handle Leakage Warnings

If `leakage_warnings` is non-empty:
1. Display each warning prominently (e.g. "WARNING: {warning}")
2. Ask the user: "Leakage detected. Continue anyway? (y/n)"
3. If user says no, STOP the workflow

If `leakage_warnings` is empty, continue silently.

---

## Phase 2: Scaffold .ml/ Directory

**Goal:** Create the experiment workspace with all required files.

### Step 2.1: Generate Run ID

```bash
RUN_ID="run-$(date -u +%Y%m%d-%H%M%S)"
echo "$RUN_ID"
```

### Step 2.2: Create Directory Structure

```bash
mkdir -p .ml/artifacts
```

### Step 2.3: Write config.json

Write `.ml/config.json` with experiment configuration:

```json
{
  "run_id": "{run_id}",
  "domain": "tabular",
  "dataset_path": "../{relative_path_to_csv}",
  "target_column": "{target_column}",
  "task": "{task}",
  "metric": "{metric}",
  "direction": "{direction}",
  "budget_experiments": 25,
  "budget_minutes": 60,
  "start_time": "{ISO timestamp}",
  "stagnation_threshold": 3,
  "draft_families": ["linear", "random_forest", "xgboost"]
}
```

Note: `dataset_path` is relative to the `.ml/` directory (typically `../dataset.csv`).
Note: `start_time` is stored in config.json so it survives context resets.

### Step 2.4: Create prepare.py (Frozen Data Pipeline)

Copy the `gsd_ml.prepare.tabular` module source into `.ml/prepare.py`:

```bash
python -c "
import inspect
from gsd_ml.prepare import tabular
print(inspect.getsource(tabular))
"
```

Write the output to `.ml/prepare.py`.

**IMPORTANT:** This file is FROZEN. The workflow must NEVER edit prepare.py.

### Step 2.5: Create train.py (Starter Template)

Read the static template from `~/.claude/gsd-ml/templates/train-tabular.py`.

Replace the 4 placeholder constants with actual values from the profile:
- `__CSV_PATH__` -> the dataset path relative to .ml/ (e.g. `../dataset.csv`)
- `__TARGET_COLUMN__` -> the target column name
- `__METRIC__` -> the metric name (e.g. `accuracy`)
- `__TASK__` -> the task type (e.g. `classification`)

Write the customized file to `.ml/train.py`.

### Step 2.6: Create Empty State Files

```bash
touch .ml/results.jsonl
touch .ml/experiments.jsonl
```

### Step 2.7: Compute Baselines

Run tabular baselines to establish the minimum bar:

```bash
cd .ml && python -c "
import json, pandas as pd
from prepare import load_data, split_data, build_preprocessor
from gsd_ml.baselines.tabular import compute_baselines
df = load_data('{dataset_path}')
X_train, X_test, y_train, y_test = split_data(df, '{target_column}')
preprocessor = build_preprocessor(X_train)
X_proc = preprocessor.fit_transform(X_train)
baselines = compute_baselines(X_proc, y_train, '{metric}', '{task}')
print(json.dumps(baselines, default=str))
"
```

Persist baselines into config.json so they survive context resets:

```bash
python -c "
import json
from pathlib import Path
config = json.loads(Path('.ml/config.json').read_text())
config['baselines'] = baselines
Path('.ml/config.json').write_text(json.dumps(config, indent=2))
"
```

Display baseline results. These are the minimum performance thresholds the model must beat.

### Step 2.8: Multi-Draft Exploration

Try 3 diverse model families to find the best starting point for iteration. Each draft gets one training run with default hyperparameters.

**Note:** The baseline gate does NOT apply during drafts. It only applies during the iteration loop (Step 3.4). During drafts, even results below baselines are kept for comparison.

**Sub-steps:**

1. Get available families from config:

```bash
python -c "
from gsd_ml.drafts import get_families_for_domain
import json

config = json.loads(open('.ml/config.json').read())
draft_families = config.get('draft_families', ['linear', 'random_forest', 'xgboost'])
families = get_families_for_domain('tabular')
selected = {k: v for k, v in families.items() if k in draft_families}
print(json.dumps(selected))
"
```

2. For each family (e.g., linear, random_forest, xgboost):
   - Edit `.ml/train.py` to use that family's model class (e.g., LogisticRegression for linear, RandomForestClassifier for random_forest, XGBClassifier for xgboost). Use default hyperparameters.
   - Run `cd .ml && python train.py 2>.ml/train.log`
   - Parse the JSON metric from stdout
   - If the run succeeded, commit: `git add .ml/ && git commit -m "draft: {family} {metric}={value}"`
   - Record the commit hash and metric value
   - If the run failed (OOM, error), record metric_value=None

3. After all drafts complete, select the best:

```bash
python -c "
import json
from gsd_ml.drafts import DraftResult, select_best_draft

drafts = [
    DraftResult(name='{family1}', metric_value={val1}, status='draft-keep', commit_hash='{hash1}', description='{desc1}'),
    DraftResult(name='{family2}', metric_value={val2}, status='draft-keep', commit_hash='{hash2}', description='{desc2}'),
    # ... one per draft that succeeded
]
best = select_best_draft(drafts, direction='{direction}')
print(json.dumps({'name': best.name, 'commit_hash': best.commit_hash, 'metric_value': best.metric_value}))
"
```

4. Checkout the best draft's train.py:

```bash
git checkout {best_commit_hash} -- .ml/train.py
```

5. Set initial state from draft results:
   - `best_metric = best_draft.metric_value`
   - `best_commit = best_draft.commit_hash`
   - Add all draft family names to `tried_families`
   - `experiment_count = number_of_drafts_run` (drafts count against budget)

6. Record all draft results in results.jsonl with status `"draft-keep"` or `"draft-discard"`:

```bash
python -c "
from pathlib import Path
from datetime import datetime, UTC
from gsd_ml.results import ResultsTracker, ExperimentResult

tracker = ResultsTracker(Path('.ml/results.jsonl'))
# For each draft:
tracker.add(ExperimentResult(
    experiment_id={N},
    commit_hash={commit_hash_repr},
    metric_name='{metric}',
    metric_value={value},
    status='{draft-keep_or_draft-discard}',
    description='Draft: {family} with default hyperparameters',
    timestamp=datetime.now(UTC).isoformat()
))
"
```

### Step 2.9: Create Git Branch

```bash
git checkout -b ml/run-{run_id}
```

### Step 2.10: Initial Commit

```bash
git add .ml/
git commit -m "scaffold: initialize .ml/ for {run_id}"
```

---

## Phase 3: Experiment Loop

**Goal:** Iteratively improve train.py, keeping improvements and reverting failures.

### Pre-Loop Setup

Initialize tracking variables:
- `experiment_count` = 0
- `keep_count` = 0
- `revert_count` = 0
- `best_metric` = None
- `best_experiment` = None
- `best_commit` = None
- Read `start_time` from `.ml/config.json`

### Loop: Repeat Until Guardrails Trip

#### Step 3.1: Guardrail Check (Before Each Iteration)

Check all guardrails before starting each experiment:

1. **Experiment count:** Read `.ml/config.json` for `budget_experiments`. If `experiment_count >= budget_experiments`, STOP with message "Experiment budget exhausted ({experiment_count}/{budget_experiments})."

2. **Time budget:** Read `start_time` from `.ml/config.json`. Calculate elapsed seconds: `now - start_time`. If elapsed >= `budget_minutes * 60`, STOP with message "Time budget exhausted ({elapsed_minutes}/{budget_minutes} minutes)."

3. **Disk space:**
   ```bash
   python -c "import shutil; u=shutil.disk_usage('.'); print(u.free/(1024**3))"
   ```
   If free disk space < 1.0 GB, STOP with message "Disk space low ({free_gb:.1f} GB free)."

4. If any guardrail trips, print which one and break the loop. This is a graceful stop, not an error.

#### Step 3.2: Edit train.py

Before editing train.py, check if `.ml/diagnostics.json` exists from the previous iteration. If it does, read it and use the findings to inform your edits:
- For classification: check `confused_pairs` (which classes are being confused), `per_class_accuracy` (which classes are underperforming), `bias` (over/under-predicting certain classes)
- For regression: check `worst_predictions` (which samples have highest error), `bias` (systematic over/under-prediction), `error_stats` (error distribution)

Use these insights to guide what you change -- e.g., if certain classes are confused, try features that distinguish them; if there's high bias, try a more expressive model.

Read the current `.ml/train.py` using the Read tool.

Edit it to try a different approach. Guidance for each iteration:
- Try different model families: RandomForest, XGBoost, LightGBM, Ridge/LogisticRegression, GradientBoosting, ExtraTrees, SVM
- Try different hyperparameters: n_estimators, max_depth, learning_rate, regularization
- Try feature engineering: polynomial features, interaction terms, binning, feature selection
- Each iteration should be meaningfully different from previous attempts

**IMPORTANT:** Only edit `.ml/train.py`. NEVER edit `.ml/prepare.py`.

#### Step 3.3: Run train.py

```bash
cd .ml && python train.py 2>.ml/train.log
```

Capture stdout. Parse the LAST line of stdout that contains valid JSON.

Extract `metric_value` and `metric_name` from the parsed JSON:
```json
{"metric_value": 0.847, "metric_name": "accuracy"}
```

If no valid JSON is found in stdout, treat this as an error. Read `.ml/train.log` for stderr output to diagnose.

#### Step 3.4: Keep/Revert Decision

Use the DeviationHandler to decide what to do with this result:

```bash
python -c "
import json
from gsd_ml.state import SessionState
from gsd_ml.guardrails import DeviationHandler

# Build result dict from train.py outcome
stderr = open('.ml/train.log').read()
if 'MemoryError' in stderr or 'OOM' in stderr:
    result = {'status': 'crash', 'error': stderr[-500:]}
elif {metric_value} is None:
    result = {'status': 'crash', 'error': 'No metric produced'}
else:
    result = {'status': 'ok', 'metric_value': {metric_value}}

state = SessionState(
    experiment_count={experiment_count},
    best_metric={best_metric_or_None},
    best_commit='{best_commit_or_empty}',
    total_keeps={keep_count},
    total_reverts={revert_count},
    run_id='{run_id}',
    task='{task}'
)

handler = DeviationHandler(direction='{direction}')
decision = handler.handle(result, state)
print(json.dumps({'decision': decision}))
"
```

Handle the decision:

**If "keep" -- apply baseline gate:**

After the DeviationHandler returns "keep", check whether the metric also beats baselines:

```bash
python -c "
import json
from pathlib import Path
from gsd_ml.baselines.tabular import passes_baseline_gate

config = json.loads(Path('.ml/config.json').read_text())
baselines = config.get('baselines', {})
if baselines and not passes_baseline_gate({metric_value}, baselines, '{direction}'):
    print('BASELINE_GATE_FAIL')
else:
    print('BASELINE_GATE_PASS')
"
```

If the baseline gate fails (output is `BASELINE_GATE_FAIL`), downgrade the decision to "revert". Log the reason: "Reverted: metric {value} does not beat baselines."

If the baseline gate passes (or no baselines exist), proceed with the keep:

- Update `best_metric = metric_value`
- Update `best_experiment = experiment_count + 1`
- Commit the improvement:
  ```bash
  cd .ml && git add . && git commit -m "exp-{N}: {metric}={value} ({brief description of what was tried})"
  ```
- Store the commit hash: `best_commit = $(git rev-parse HEAD)`
- Increment `keep_count`

**If "revert":**
- Revert ONLY train.py:
  ```bash
  cd .ml && git checkout -- train.py
  ```
- **IMPORTANT:** Do NOT revert results.jsonl, experiments.jsonl, or checkpoint.json. These are append-only state files that must survive reverts.
- Increment `revert_count`

**If "retry":**
- The run failed due to OOM (Out of Memory)
- Edit train.py to reduce resource usage:
  - Reduce n_estimators, max_depth, or batch_size
  - Use a simpler model
  - Reduce dataset size with sampling
- Re-run train.py (go back to Step 3.3)
- Track retry count; DeviationHandler will return "stop" after 3 retries

**If "stop":**
- Repeated OOM failures; the system cannot handle this workload
- Print the reason and break the experiment loop
- This is a graceful stop, not an error

#### Step 3.5a: Run Diagnostics

After each experiment (regardless of keep/revert), if `.ml/predictions.csv` exists, run diagnostics:

```bash
python -c "
import json, pandas as pd
from pathlib import Path
from gsd_ml.diagnostics import diagnose_regression, diagnose_classification

preds_path = Path('.ml/predictions.csv')
if not preds_path.exists():
    print('No predictions.csv found, skipping diagnostics')
else:
    preds = pd.read_csv(preds_path)
    config = json.loads(Path('.ml/config.json').read_text())
    task = config['task']
    if task == 'classification':
        diag = diagnose_classification(preds['y_true'].values, preds['y_pred'].values)
    else:
        diag = diagnose_regression(preds['y_true'].values, preds['y_pred'].values)
    Path('.ml/diagnostics.json').write_text(json.dumps(diag, indent=2, default=str))
    print(json.dumps(diag, default=str))
"
```

Display the diagnostics summary. Note: `diagnostics.json` is ephemeral (overwritten each iteration), NOT saved in checkpoint.

#### Step 3.5b: Record Results

After each experiment (regardless of keep/revert decision), record:

**Append to results.jsonl:**

```bash
python -c "
from pathlib import Path
from datetime import datetime, UTC
from gsd_ml.results import ResultsTracker, ExperimentResult

tracker = ResultsTracker(Path('.ml/results.jsonl'))
tracker.add(ExperimentResult(
    experiment_id={N},
    commit_hash={commit_hash_repr},
    metric_name='{metric}',
    metric_value={value},
    status='{keep_or_revert}',
    description='{what was tried}',
    timestamp=datetime.now(UTC).isoformat()
))
"
```

**Append journal entry and update experiments.md:**

```bash
python -c "
from pathlib import Path
from gsd_ml.journal import JournalEntry, append_journal_entry, load_journal, render_journal_markdown

entry = JournalEntry(
    experiment_id={N},
    hypothesis='{what was tried and why}',
    result='{outcome description}',
    metric_value={value},
    metric_delta={delta_or_None},
    commit_hash={commit_hash_repr},
    status='{keep_or_revert}'
)
append_journal_entry(Path('.ml/experiments.jsonl'), entry)
entries = load_journal(Path('.ml/experiments.jsonl'))
md = render_journal_markdown(entries)
Path('.ml/experiments.md').write_text(md)
"
```

**Save checkpoint:**

```bash
python -c "
import json
from pathlib import Path
from gsd_ml.state import SessionState
from gsd_ml.checkpoint import save_checkpoint
config = json.loads(Path('.ml/config.json').read_text())
state = SessionState(
    run_id='{run_id}',
    experiment_count={N},
    total_keeps={keeps},
    total_reverts={reverts},
    best_metric={best_metric_or_None},
    best_commit='{best_commit_or_empty}',
    task='{task}',
    baselines=config.get('baselines')
)
save_checkpoint(state, Path('.ml'))
"
```

#### Step 3.6: Increment and Continue

Increment `experiment_count` by 1. Return to Step 3.1.

---

## Phase 4: Finalize

**Goal:** Export the best model, generate a retrospective, and tag the best commit.

This phase runs after the experiment loop ends (guardrail trip, stop decision, or all experiments complete).

### Step 4.1: Export Best Model

If `best_metric` is not None (at least one successful experiment):

```bash
python -c "
import json
from pathlib import Path
from gsd_ml.state import SessionState
from gsd_ml.export import export_artifact

state = SessionState(
    experiment_count={experiment_count},
    best_metric={best_metric},
    best_commit='{best_commit}',
    total_keeps={keep_count},
    total_reverts={revert_count},
    run_id='{run_id}',
    task='{task}'
)
config = json.loads(Path('.ml/config.json').read_text())
result = export_artifact(Path('.ml'), state, config)
if result:
    print(f'Exported to {result}')
else:
    print('No model artifact found to export')
"
```

If no experiments succeeded (best_metric is None), skip export and note it in the retrospective.

### Step 4.2: Generate Retrospective

Calculate elapsed time: `duration_minutes = (now - start_time) / 60`

```bash
python -c "
import json
from pathlib import Path
from gsd_ml.state import SessionState
from gsd_ml.results import ResultsTracker
from gsd_ml.retrospective import generate_retrospective

tracker = ResultsTracker(Path('.ml/results.jsonl'))
state = SessionState(
    experiment_count={experiment_count},
    best_metric={best_metric_or_None},
    best_commit='{best_commit_or_empty}',
    total_keeps={keep_count},
    total_reverts={revert_count},
    run_id='{run_id}',
    cost_spent_usd=0.0,
    task='{task}'
)
config = json.loads(Path('.ml/config.json').read_text())
md = generate_retrospective(tracker, state, config)
Path('.ml/RETROSPECTIVE.md').write_text(md)
print('Retrospective written to .ml/RETROSPECTIVE.md')
"
```

### Step 4.3: Tag Best Commit

If `best_commit` is not empty:

```bash
git tag ml-best-{run_id} {best_commit}
```

### Step 4.4: Final Commit

```bash
cd .ml && git add . && git commit -m "finalize: {run_id} complete, best {metric}={best_metric}"
```

### Step 4.5: Print Summary

Display final results:

```
=== ML Run Complete ===
Run ID:       {run_id}
Experiments:  {experiment_count}
Keeps:        {keep_count}
Reverts:      {revert_count}
Best Metric:  {metric} = {best_metric} (experiment {best_experiment})
Best Commit:  {best_commit}
Duration:     {elapsed_minutes:.1f} minutes
Branch:       ml/run-{run_id}
Tag:          ml-best-{run_id}
```

---

## Important Rules

These rules apply throughout the entire workflow:

1. **NEVER modify prepare.py** -- it is the frozen data pipeline. Only train.py is mutable.

2. **Selective revert only** -- On non-improvement, only revert train.py:
   ```bash
   git checkout -- train.py
   ```
   NEVER revert results.jsonl, experiments.jsonl, checkpoint.json, or experiments.md.

3. **Working directory** -- Always run train.py from .ml/:
   ```bash
   cd .ml && python train.py
   ```
   train.py uses paths relative to .ml/ (e.g. `../dataset.csv`).

4. **JSON output parsing** -- Parse the LAST line of stdout that contains valid JSON. Libraries (sklearn, xgboost, lightgbm) may print warnings or progress info before the JSON line.

5. **start_time persistence** -- Read `start_time` from `.ml/config.json` for guardrail checks. Do NOT rely on in-memory timers, which reset between context windows.

6. **CSV path** -- The CSV path in train.py and config.json is relative to the `.ml/` directory (typically `../dataset.csv`).

7. **Git branch** -- The branch `ml/run-{run_id}` must be created BEFORE the first experiment commit. All experiment commits go on this branch, never on main.

8. **State files** -- checkpoint.json, results.jsonl, and experiments.jsonl are the source of truth. They must be committed with keeps and never reverted.
