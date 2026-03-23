# ML Status Workflow
> Shows experiment run status and metrics from the .ml/ directory.
> Called by /gsd:ml-status skill. Do not run directly.

---

## Pre-flight Checks

Verify the Python package is available:

```bash
python3 -c "import gsd_ml; print('OK')" 2>&1
```

If this fails (ModuleNotFoundError), STOP and tell the user:
> gsd_ml Python package is not installed. Install with: `pip install gsd-ml` (from PyPI) or `pip install ./python` (from repo)

---

## Step 1: Validate Experiment Directory

Check for `.ml/` directory in the current working directory:

```bash
test -d .ml/ || echo "NO_ML_DIR"
```

If `.ml/` does not exist, print:

```
No experiment directory found. Run /gsd:ml first.
```

Then STOP. Do not proceed.

---

## Step 2: Load State

Load experiment state using Python one-liners. Run this single script:

```bash
python3 -c "
import json, sys
from pathlib import Path

ml = Path('.ml')

# Load checkpoint
state = None
try:
    from gsd_ml.checkpoint import load_checkpoint
    state = load_checkpoint(ml)
except Exception:
    pass

# Load config
config = {}
try:
    config = json.loads((ml / 'config.json').read_text())
except Exception:
    pass

# Load results
results = []
try:
    from gsd_ml.results import ResultsTracker
    tracker = ResultsTracker(ml / 'results.jsonl')
    results = tracker.results
except Exception:
    pass

if state is None and not results:
    print('NO_DATA')
    sys.exit(0)

# Output as JSON for parsing
output = {
    'run_id': getattr(state, 'run_id', 'unknown') if state else 'unknown',
    'experiment_count': getattr(state, 'experiment_count', 0) if state else len(results),
    'best_metric': getattr(state, 'best_metric', None) if state else None,
    'total_keeps': getattr(state, 'total_keeps', 0) if state else 0,
    'total_reverts': getattr(state, 'total_reverts', 0) if state else 0,
    'cost_spent_usd': getattr(state, 'cost_spent_usd', 0.0) if state else 0.0,
    'task': getattr(state, 'task', 'unknown') if state else config.get('task', 'unknown'),
    'domain': config.get('domain', 'unknown'),
    'metric': config.get('metric', 'unknown'),
    'direction': config.get('direction', 'unknown'),
    'budget_experiments': config.get('budget_experiments', 0),
    'budget_minutes': config.get('budget_minutes', 0),
    'start_time': config.get('start_time', ''),
    'results': [{'metric_value': r.get('metric_value', r.get('value', None)), 'iteration': i+1} for i, r in enumerate(results)] if results else []
}
print(json.dumps(output))
"
```

If the output is `NO_DATA`, print:

```
No experiments recorded yet.
```

Then STOP.

Parse the JSON output and store the fields for formatting.

---

## Step 3: Summary View (Default)

If the user did NOT pass `--detail`, display the summary table.

Format and print using the loaded state data:

```
== Experiment Status ==

Run ID   | Domain  | Metric    | Best     | Exps | Keeps/Reverts | Cost    | Started          | Duration  | Time/Exp
---------+---------+-----------+----------+------+---------------+---------+------------------+-----------+---------
{run_id} | {domain}| {metric}  | {best}   | {n}  | {k}/{r}       | ${cost} | {start_time}     | {dur}     | {t_per}
```

Compute derived values:
- **Duration:** From `start_time` to now (use Python `datetime`). Format as `Xh Ym` or `Xm`.
- **Time/Exp:** Duration in minutes / experiment_count. Format as `X.Ym`.
- **Best metric:** Format to 4 decimal places.
- **Cost:** Format as `$X.XX`.

Use plain Python string formatting. No external libraries beyond stdlib.

---

## Step 4: Detail View (--detail flag)

If the user passes `--detail` or `--detail <run_id>`, show the detailed view.

### 4a: Full Summary Fields

Print all state fields in markdown format:

```markdown
## Experiment Detail: {run_id}

| Field             | Value                |
|-------------------|----------------------|
| Domain            | {domain}             |
| Task              | {task}               |
| Metric            | {metric} ({direction}) |
| Best Value        | {best_metric:.4f}    |
| Experiments       | {experiment_count}   |
| Keeps / Reverts   | {total_keeps} / {total_reverts} |
| Cost              | ${cost_spent_usd:.2f} |
| Budget (exps)     | {budget_experiments} |
| Budget (minutes)  | {budget_minutes}     |
| Started           | {start_time}         |
| Duration          | {computed_duration}  |
```

### 4b: Experiment Journal

If `.ml/experiments.md` exists, print its contents:

```bash
cat .ml/experiments.md
```

### 4c: ASCII Metric Trajectory

Using the results list from Step 2, print an ASCII bar chart showing metric value per experiment iteration.

Generate with Python:

```bash
python3 -c "
import json, sys

results_json = sys.argv[1]
metric_name = sys.argv[2]
direction = sys.argv[3]

results = json.loads(results_json)
if not results:
    print('No results to chart.')
    sys.exit(0)

values = [r['metric_value'] for r in results if r['metric_value'] is not None]
if not values:
    print('No metric values recorded.')
    sys.exit(0)

max_val = max(values)
min_val = min(values)
width = 40

print()
print(f'  {metric_name} ({\"higher\" if direction == \"maximize\" else \"lower\"} is better)')
print(f'  {\"=\" * (width + 20)}')

for i, v in enumerate(values, 1):
    if max_val > 0:
        bar_len = int((v / max_val) * width)
    else:
        bar_len = 0
    bar_len = max(1, bar_len)
    print(f'  {i:>4} | {\"#\" * bar_len} {v:.4f}')

print()
" '{results_json}' '{metric_name}' '{direction}'
```

Replace `{results_json}`, `{metric_name}`, and `{direction}` with the actual values from Step 2.

---

## Notes

- This workflow is scoped to the current `.ml/` directory only. It does not scan parent or sibling directories.
- All data comes from `.ml/checkpoint.json`, `.ml/config.json`, and `.ml/results.jsonl`.
- No modifications are made to any files -- this is a read-only operation.
