# ML Resume Workflow
> Restores experiment state from checkpoint and re-enters the experiment loop.
> Called by /gsd:ml-resume skill. Do not run directly.

---

## Pre-flight Checks

Verify the Python package is available:

```bash
python3 -c "import gsd_ml; print('OK')" 2>&1
```

If this fails (ModuleNotFoundError), STOP and tell the user:
> gsd_ml Python package is not installed. Install with: `pip install gsd-ml` (from PyPI) or `pip install ./python` (from repo)

Verify this is a git repository:

```bash
git status --porcelain 2>&1
```

If git is not available or the directory is not a git repo, STOP and tell the user:
> This directory must be a git repository. Run `git init` first.

---

## Step 1: Validate Checkpoint Exists

Check that the `.ml/` directory and checkpoint file exist:

```bash
test -d .ml/ && test -f .ml/checkpoint.json && echo "OK" || echo "MISSING"
```

If either is missing, print:
```
No experiment checkpoint found. Run /gsd:ml first.
```
Then STOP. Do not proceed.

---

## Step 2: Load Checkpoint

Load the checkpoint using the gsd_ml checkpoint module:

```bash
python3 -c "
from pathlib import Path
from gsd_ml.checkpoint import load_checkpoint
import json

state = load_checkpoint(Path('.ml'))
if state is None:
    print('ERROR: Checkpoint is empty or corrupt')
else:
    print(json.dumps({
        'run_id': state.run_id,
        'experiment_count': state.experiment_count,
        'best_metric': state.best_metric,
        'best_commit': state.best_commit,
        'total_keeps': state.total_keeps,
        'total_reverts': state.total_reverts,
        'cost_spent_usd': state.cost_spent_usd,
        'task': state.task,
        'baselines': state.baselines,
        'consecutive_reverts': state.consecutive_reverts,
        'tried_families': list(state.tried_families) if state.tried_families else []
    }, indent=2))
"
```

If the checkpoint is empty or corrupt, STOP with an error message.

If `--run <run_id>` was provided, verify the checkpoint's `run_id` matches. If it does not match, check `.ml/results.jsonl` for an entry with the specified run_id. If no match found, print:
```
ERROR: No checkpoint found for run_id '{run_id}'. Available: {checkpoint_run_id}
```
Then STOP.

Store all returned fields as variables for the rest of the workflow.

---

## Step 3: Load Config

Read `.ml/config.json` to restore experiment configuration:

```bash
cat .ml/config.json
```

Extract and store these fields:
- `domain` -- "tabular", "dl", or "ft"
- `metric` -- the evaluation metric name
- `direction` -- "maximize" or "minimize"
- `dataset_path` -- path to the dataset
- `target_column` -- target column name (may be null for FT)
- `model_name` -- HuggingFace/timm model name (DL/FT only, may be null)
- `budget_experiments` -- max number of experiments allowed
- `budget_minutes` -- max wall-clock minutes allowed
- `start_time` -- original experiment start time (ISO format)

---

## Step 4: Check Budget

Run guardrails to check if the budget is exhausted:

```bash
python3 -c "
from pathlib import Path
from gsd_ml.guardrails import ResourceGuardrails
from gsd_ml.state import SessionState
import json

with open('.ml/config.json') as f:
    config = json.load(f)

guardrails = ResourceGuardrails(config, Path('.ml'))
state = SessionState(
    experiment_count=config.get('experiment_count', 0),
    run_id=config.get('run_id', '')
)
stop = guardrails.should_stop(state)
reason = guardrails.stop_reason(state) if stop else None
print(json.dumps({'stop': stop, 'reason': reason}))
"
```

**If budget is NOT exhausted** (`"stop": false`): Continue to Step 5.

**If budget IS exhausted** (`"stop": true`):

1. Print current state:
```
Budget exhausted: {experiment_count} experiments run, budget was {budget_experiments} experiments / {budget_minutes} minutes.
Best result: {best_metric} ({metric}, {direction})
```

2. Ask the user:
```
Budget exhausted. How many additional experiments would you like to add? (Enter a number, or 'cancel' to abort)
```

3. If user provides a number N:
   - Read `.ml/config.json`
   - Add N to `budget_experiments`
   - If time budget was also exhausted, add proportional minutes: `additional_minutes = N * (budget_minutes / budget_experiments)`
   - **IMPORTANT: Do NOT reset `start_time`** -- only increase `budget_experiments` and/or `budget_minutes`
   - Write updated config back to `.ml/config.json`

4. If user says 'cancel': STOP.

---

## Step 5: Checkout Experiment Branch

Verify and checkout the experiment branch:

```bash
git branch --list "ml/run-{run_id}"
```

**If branch exists:**
```bash
git checkout "ml/run-{run_id}"
```

**If branch does NOT exist** (e.g., branch was cleaned up):
```bash
git checkout -b "ml/run-{run_id}"
```

Confirm the branch is active:
```bash
git branch --show-current
```

---

## Step 6: Print Restoration Summary

Display what was restored:

```
Resuming experiment: {run_id}
  Domain: {domain}
  Metric: {metric} ({direction})
  Progress: {experiment_count} experiments ({total_keeps} keeps, {total_reverts} reverts)
  Best: {best_metric}
  Budget remaining: {budget_experiments - experiment_count} experiments
  Branch: ml/run-{run_id}
```

---

## Step 7: Re-enter Experiment Loop

Now follow `ml-run.md` starting at **Phase 3: Experiment Loop**.

Use the restored variables:
- All SessionState fields (`run_id`, `experiment_count`, `best_metric`, `best_commit`, `total_keeps`, `total_reverts`, `cost_spent_usd`, `task`, `baselines`, `consecutive_reverts`, `tried_families`)
- Config values for guardrail checks (`budget_experiments`, `budget_minutes`, `start_time`, `domain`, `metric`, `direction`)
- The existing `.ml/train.py` as the starting point (it already contains the best iteration's code on this branch)

**Do NOT re-run Phase 1 (Profile Dataset) or Phase 2 (Scaffold) from ml-run.md.**

---

## Key Pitfalls

- **NEVER reset `start_time` when extending budget.** The `start_time` in `config.json` records when the experiment originally began. Budget extension only increases `budget_experiments` and/or `budget_minutes`. Resetting `start_time` would make the time-based guardrail meaningless.
- **ALWAYS checkout the correct branch before resuming.** All experiment commits must land on the `ml/run-{run_id}` branch, not on main or any other branch.
- **Trust the checkpoint.** Do not re-run the last experiment to verify the checkpoint is accurate. The checkpoint was written after successful metric parsing and represents the true state.
