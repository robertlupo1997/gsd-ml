# ML Diagnose Workflow
> Runs diagnostics on the best model from the last experiment.
> Called by /gsd:ml-diagnose skill. Do not run directly.

---

## Step 1: Pre-flight and State Validation

Verify the Python package is available:

```bash
python3 -c "import gsd_ml; print('OK')" 2>&1
```

If this fails (ModuleNotFoundError), STOP and tell the user:
> gsd_ml Python package is not installed. Install with: `pip install gsd-ml` (from PyPI) or `pip install ./python` (from repo)

Load `.ml/` checkpoint and validate:

```bash
python3 -c "
from pathlib import Path
from gsd_ml.checkpoint import load_checkpoint
import json, sys

ml = Path('.ml')
if not ml.exists():
    print('NO_ML_DIR')
    sys.exit(0)

state = load_checkpoint(ml)
if state is None:
    print('NO_CHECKPOINT')
    sys.exit(0)

best_commit = getattr(state, 'best_commit', None)
if not best_commit:
    print('NO_BEST')
    sys.exit(0)

print(json.dumps({
    'best_commit': best_commit,
    'task': getattr(state, 'task', 'unknown'),
    'run_id': getattr(state, 'run_id', 'unknown')
}))
"
```

Handle each case:
- `NO_ML_DIR`: Print "No experiment directory found. Run /gsd:ml first." and STOP.
- `NO_CHECKPOINT`: Print "No experiment results found." and STOP.
- `NO_BEST`: Print "No best model commit recorded yet." and STOP.

Parse the JSON output and store `best_commit`, `task`, and `run_id`.

---

## Step 2: Read Config

Load domain, metric, and task from config:

```bash
python3 -c "
import json
config = json.loads(open('.ml/config.json').read())
print(json.dumps({
    'domain': config.get('domain', 'tabular'),
    'metric': config.get('metric', 'unknown'),
    'direction': config.get('direction', 'maximize'),
    'task': config.get('task', 'unknown')
}))
"
```

Parse the JSON and store the config fields. Use the config `task` if Step 1's task was `unknown`.

---

## Step 3: Check for Existing Predictions

```bash
test -f .ml/predictions.csv && echo "EXISTS" || echo "MISSING"
```

If `EXISTS`, skip to Step 5 (use existing predictions).
If `MISSING`, proceed to Step 4.

---

## Step 4: Generate Predictions

### 4a: Save Current Branch

```bash
CURRENT=$(git rev-parse --abbrev-ref HEAD)
echo "$CURRENT"
```

Store the current branch name.

### 4b: Checkout Best Model's train.py

```bash
git checkout {best_commit} -- .ml/train.py
```

Replace `{best_commit}` with the actual commit hash from Step 1.

### 4c: Run train.py to Generate Predictions

Run the training script. It should produce `.ml/predictions.csv` as part of its evaluation phase.

```bash
cd .ml && python3 train.py 2>&1
```

### 4d: Restore Current train.py

```bash
git checkout {current_branch} -- .ml/train.py 2>/dev/null || git checkout HEAD -- .ml/train.py
```

Replace `{current_branch}` with the branch name saved in 4a.

**Important:** Always restore, even if train.py execution failed. If checkout fails (detached HEAD), use `git checkout HEAD -- .ml/train.py`.

---

## Step 5: Run Diagnostics

Run the appropriate diagnostic function based on task type:

```bash
python3 -c "
import pandas as pd
import json, sys

task = '{task}'
df = pd.read_csv('.ml/predictions.csv')

# Expect columns: y_true, y_pred (and optionally y_prob for classification)
y_true = df['y_true'].values
y_pred = df['y_pred'].values

if task in ('classification', 'image_classification', 'text_classification'):
    from gsd_ml.diagnostics import diagnose_classification
    results = diagnose_classification(y_true, y_pred)
else:
    from gsd_ml.diagnostics import diagnose_regression
    results = diagnose_regression(y_true, y_pred)

print(json.dumps(results, default=str))
"
```

Replace `{task}` with the actual task value from Steps 1-2.

Parse the JSON output containing diagnostic results.

---

## Step 6: Format Output

Print a formatted diagnostic report to the terminal.

### 6a: Header

```markdown
## Diagnostic Report: {run_id}

**Task:** {task} | **Metric:** {metric} ({direction}) | **Domain:** {domain}
```

### 6b: Worst Predictions

Format the `worst_predictions` from diagnostics as a table (top 10 by error magnitude):

```markdown
### Worst Predictions

| # | True Value | Predicted | Error    |
|---|------------|-----------|----------|
| 1 | {true}     | {pred}    | {error}  |
```

### 6c: Bias Analysis

Print overall bias metrics:

```markdown
### Bias Analysis

- **Mean Error:** {mean_error}
- **Median Error:** {median_error}
- **Error Std Dev:** {std_error}
```

For classification tasks, also show per-class accuracy if available.

### 6d: Feature-Error Correlations (if available)

If the diagnostics returned feature correlations:

```markdown
### Feature-Error Correlations

| Feature       | Correlation |
|---------------|-------------|
| {feature}     | {corr}      |
```

### 6e: Confused Class Pairs (classification only)

For classification tasks, show the most confused pairs:

```markdown
### Most Confused Class Pairs

| Class A | Class B | Confusion Count |
|---------|---------|-----------------|
| {a}     | {b}     | {count}         |
```

### 6f: Suggested Actions

Based on the diagnostic findings, print actionable suggestions:

```markdown
## Suggested Actions

Based on the diagnostic analysis:
```

Apply these rules to generate suggestions:
- **High error on specific class** -> "Try class weighting or oversampling for class {X}"
- **Large residuals on high values** -> "Try log-transforming the target variable"
- **Systematic over-prediction** -> "Model has positive bias; try adjusting threshold or adding regularization"
- **Systematic under-prediction** -> "Model has negative bias; try removing regularization or increasing capacity"
- **High feature-error correlation** -> "Feature {X} correlates with errors; try engineering interactions or non-linear transforms"
- **Confused class pairs** -> "Classes {A} and {B} are frequently confused; consider merging or adding distinguishing features"
- **High variance in errors** -> "Prediction quality is inconsistent; try ensemble methods or more training data"

Print 2-5 of the most relevant suggestions based on actual findings.

---

## Notes

- This workflow always saves and restores git state. The current branch is never left in a modified state.
- Predictions come from `.ml/predictions.csv` (either pre-existing or generated in Step 4).
- For fine-tuning tasks with loss/perplexity metrics, diagnostics may not be applicable. In that case, print: "Diagnostics not available for fine-tuning tasks with loss/perplexity metrics."
- All diagnostic functions are from `gsd_ml.diagnostics` (ported in Phase 1).
