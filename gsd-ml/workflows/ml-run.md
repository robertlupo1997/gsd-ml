# ML Run Workflow
> Orchestrates a complete ML experiment: profile, scaffold, loop, finalize.
> Called by /gsd:ml skill. Do not run directly.

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

## Phase 1: Profile Dataset

**Goal:** Understand the dataset before building anything.

### Step 1.1: Parse Arguments

Extract from the skill invocation:
- `dataset_path` -- path to the CSV file (tabular), image directory (DL image), or data file (DL text, FT)
- `target_column` -- name of the target column (tabular, DL text) or None (DL image uses subdirectory names, FT has no target)
- `domain` -- defaults to `"tabular"`. Valid values: `"tabular"`, `"dl"`, `"ft"`
- `task` -- (DL only) `"image_classification"` or `"text_classification"`. Ignored for tabular/ft.
- `model_name` -- (FT required, DL optional) HuggingFace model name (e.g. `"meta-llama/Llama-2-7b-hf"`) or timm model name (e.g. `"resnet50"`)

### Step 1.2: Verify Dataset Exists

**If domain == "tabular":**

```bash
test -f {dataset_path} || echo "ERROR: Dataset not found at {dataset_path}"
```

If the file does not exist, STOP and report the error. Do not proceed.

**If domain == "dl":**

For `task == "image_classification"`: verify the dataset path is a directory with subdirectories (one per class):

```bash
test -d {dataset_path} || echo "ERROR: Image directory not found at {dataset_path}"
ls -d {dataset_path}/*/ 2>/dev/null | head -5 || echo "ERROR: No class subdirectories found in {dataset_path}"
```

For `task == "text_classification"`: verify the data file exists (CSV or JSON):

```bash
test -f {dataset_path} || echo "ERROR: Text data file not found at {dataset_path}"
```

If verification fails, STOP and report the error. Do not proceed.

**If domain == "ft":**

Verify the data file exists (JSONL, JSON, or CSV):

```bash
test -f {dataset_path} || echo "ERROR: Data file not found at {dataset_path}"
```

If the file does not exist, STOP and report the error. Do not proceed.

### Step 1.3: Profile the Dataset

**If domain == "tabular":**

Run the profiler to auto-detect task type, metric, and dataset statistics:

```bash
python3 -c "
import json, pandas as pd
from gsd_ml.profiler import profile_dataset
from dataclasses import asdict
df = pd.read_csv('{dataset_path}')
profile = profile_dataset(df, '{target_column}')
print(json.dumps(asdict(profile), default=str))
"
```

**If domain == "dl" and task == "image_classification":**

Count subdirectories as classes, count images, set defaults:

```bash
python3 -c "
import json
from pathlib import Path

data_dir = Path('{dataset_path}')
class_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])
num_classes = len(class_dirs)
total_images = sum(len(list(d.glob('*.*'))) for d in class_dirs)
class_names = [d.name for d in class_dirs]

profile = {
    'task': 'image_classification',
    'metric': 'accuracy',
    'direction': 'maximize',
    'num_classes': num_classes,
    'total_images': total_images,
    'class_names': class_names,
}
print(json.dumps(profile))
"
```

Set: `task = "image_classification"`, `metric = "accuracy"`, `direction = "maximize"`.

**If domain == "dl" and task == "text_classification":**

Read the CSV/JSON file, detect number of labels:

```bash
python3 -c "
import json, pandas as pd
from pathlib import Path

path = Path('{dataset_path}')
if path.suffix == '.json':
    df = pd.read_json(path)
else:
    df = pd.read_csv(path)

num_labels = df['{target_column}'].nunique()
n_rows = len(df)
label_dist = df['{target_column}'].value_counts().to_dict()

profile = {
    'task': 'text_classification',
    'metric': 'f1_weighted',
    'direction': 'maximize',
    'num_labels': num_labels,
    'n_rows': n_rows,
    'label_distribution': {str(k): v for k, v in label_dist.items()},
}
print(json.dumps(profile))
"
```

Set: `task = "text_classification"`, `metric = "f1_weighted"`, `direction = "maximize"`.

**If domain == "ft":**

Skip profiling entirely. Set defaults:

- `task = "sft"`
- `metric = "perplexity"` (or user-specified; valid options: `"perplexity"`, `"loss"`, `"rouge1"`, `"rouge2"`, `"rougeL"`)
- `direction = "minimize"` (except ROUGE metrics which are `"maximize"`)

### Step 1.3a: GPU Check (DL and FT Only)

**Skip this step if domain == "tabular".**

For DL and FT domains, check GPU availability early:

```bash
python3 -c "
from gsd_ml.prepare.deeplearning import get_device_info
import json
info = get_device_info()
print(json.dumps(info))
"
```

If the device is `"cpu"`, print a prominent warning:

```
WARNING: No GPU detected. DL/FT training will be very slow.
Consider using a GPU-enabled machine for better performance.
```

Do NOT block the workflow -- just warn and continue.

### Step 1.4: Parse Profile Output

**If domain == "tabular":**

Extract from the JSON output:
- `task` -- "classification" or "regression"
- `metric` -- e.g. "accuracy", "f1", "f1_weighted", "r2", "rmse", "mae"
- `direction` -- "maximize" or "minimize"
- `n_rows` -- number of rows
- `n_features` -- number of features
- `missing_pct` -- percentage of missing values
- `leakage_warnings` -- list of leakage warnings (may be empty)

**If domain == "dl":**

Extract from the profile output:
- `task` -- "image_classification" or "text_classification"
- `metric` -- "accuracy" (image) or "f1_weighted" (text)
- `direction` -- "maximize"
- For image: `num_classes`, `total_images`, `class_names`
- For text: `num_labels`, `n_rows`, `label_distribution`

**If domain == "ft":**

No profiling output to parse. Use the defaults set in Step 1.3.

### Step 1.5: Display Profile Summary

**If domain == "tabular":**

```
Dataset Profile:
  Rows: {n_rows}
  Features: {n_features}
  Task: {task}
  Metric: {metric} ({direction})
  Missing: {missing_pct}%
  Leakage warnings: {len(leakage_warnings)}
```

**If domain == "dl" and task == "image_classification":**

```
Dataset Profile:
  Domain: Deep Learning (Image Classification)
  Classes: {num_classes}
  Total Images: {total_images}
  Class Names: {class_names}
  Metric: {metric} ({direction})
```

**If domain == "dl" and task == "text_classification":**

```
Dataset Profile:
  Domain: Deep Learning (Text Classification)
  Rows: {n_rows}
  Labels: {num_labels}
  Label Distribution: {label_distribution}
  Metric: {metric} ({direction})
```

**If domain == "ft":**

```
Dataset Profile:
  Domain: Fine-Tuning (SFT)
  Model: {model_name}
  Data: {dataset_path}
  Task: sft
  Metric: {metric} ({direction})
```

### Step 1.6: Handle Leakage Warnings

**If domain == "tabular":**

If `leakage_warnings` is non-empty:
1. Display each warning prominently (e.g. "WARNING: {warning}")
2. Ask the user: "Leakage detected. Continue anyway? (y/n)"
3. If user says no, STOP the workflow

If `leakage_warnings` is empty, continue silently.

**If domain == "dl" or domain == "ft":**

Skip this step -- leakage detection is not applicable to DL/FT domains.

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

**If domain == "tabular":**

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

**If domain == "dl":**

```json
{
  "run_id": "{run_id}",
  "domain": "dl",
  "dataset_path": "../{relative_path_to_data}",
  "target_column": "{target_column_or_null}",
  "task": "{image_classification|text_classification}",
  "metric": "{metric}",
  "direction": "{direction}",
  "model_name": "{model_name_or_default}",
  "img_size": 224,
  "budget_experiments": 15,
  "budget_minutes": 120,
  "start_time": "{ISO timestamp}",
  "stagnation_threshold": 3,
  "draft_families": ["resnet", "vit", "efficientnet"]
}
```

Note: `img_size` is only relevant for image_classification. For text_classification, it can be omitted or ignored.

**If domain == "ft":**

```json
{
  "run_id": "{run_id}",
  "domain": "ft",
  "dataset_path": "../{relative_path_to_data}",
  "task": "sft",
  "metric": "{metric}",
  "direction": "{direction}",
  "model_name": "{model_name}",
  "lora_r": 8,
  "lora_alpha": 8,
  "max_length": 512,
  "learning_rate": 2e-4,
  "num_epochs": 3,
  "budget_experiments": 10,
  "budget_minutes": 120,
  "start_time": "{ISO timestamp}",
  "stagnation_threshold": 3,
  "draft_families": ["qlora_r8", "qlora_r16", "qlora_r32"]
}
```

Note: `dataset_path` is relative to the `.ml/` directory (typically `../dataset.csv` or `../data.jsonl`).
Note: `start_time` is stored in config.json so it survives context resets.

### Step 2.4: Create prepare.py (Frozen Data Pipeline)

**If domain == "tabular":**

Copy the `gsd_ml.prepare.tabular` module source into `.ml/prepare.py`:

```bash
python3 -c "
import inspect
from gsd_ml.prepare import tabular
print(inspect.getsource(tabular))
"
```

**If domain == "dl":**

Copy the `gsd_ml.prepare.deeplearning` module source into `.ml/prepare.py`:

```bash
python3 -c "
import inspect
from gsd_ml.prepare import deeplearning
print(inspect.getsource(deeplearning))
"
```

**If domain == "ft":**

Copy the `gsd_ml.prepare.finetuning` module source into `.ml/prepare.py`:

```bash
python3 -c "
import inspect
from gsd_ml.prepare import finetuning
print(inspect.getsource(finetuning))
"
```

Write the output to `.ml/prepare.py`.

**IMPORTANT:** This file is FROZEN. The workflow must NEVER edit prepare.py.

### Step 2.5: Create train.py (Starter Template)

**If domain == "tabular":**

Read the static template from `~/.claude/gsd-ml/templates/train-tabular.py`.

Replace the 4 placeholder constants with actual values from the profile:
- `__CSV_PATH__` -> the dataset path relative to .ml/ (e.g. `../dataset.csv`)
- `__TARGET_COLUMN__` -> the target column name
- `__METRIC__` -> the metric name (e.g. `accuracy`)
- `__TASK__` -> the task type (e.g. `classification`)

**If domain == "dl" and task == "image_classification":**

Read the static template from `~/.claude/gsd-ml/templates/train-dl-image.py`.

Replace the placeholder constants with actual values:
- `__DATA_PATH__` -> the image directory path relative to .ml/ (e.g. `../images/`)
- `__METRIC__` -> the metric name (e.g. `accuracy`)
- `__MODEL_NAME__` -> the model name (e.g. `resnet50`)
- `__IMG_SIZE__` -> the image size (e.g. `224`)
- `__BATCH_SIZE__` -> the batch size (e.g. `32`)
- `__TIME_BUDGET_SEC__` -> time budget in seconds (e.g. `3600`)

**If domain == "dl" and task == "text_classification":**

Read the static template from `~/.claude/gsd-ml/templates/train-dl-text.py`.

Replace the placeholder constants with actual values:
- `__DATA_PATH__` -> the text data file path relative to .ml/ (e.g. `../data.csv`)
- `__METRIC__` -> the metric name (e.g. `f1_weighted`)
- `__MODEL_NAME__` -> the model name (e.g. `distilbert-base-uncased`)
- `__BATCH_SIZE__` -> the batch size (e.g. `16`)
- `__TIME_BUDGET_SEC__` -> time budget in seconds (e.g. `3600`)

**If domain == "ft":**

Read the static template from `~/.claude/gsd-ml/templates/train-ft.py`.

Replace the placeholder constants with actual values:
- `__DATA_PATH__` -> the data file path relative to .ml/ (e.g. `../data.jsonl`)
- `__MODEL_NAME__` -> the HuggingFace model name (e.g. `meta-llama/Llama-2-7b-hf`)
- `__METRIC__` -> the metric name (e.g. `perplexity`)
- `__LORA_R__` -> LoRA rank (e.g. `8`)
- `__LORA_ALPHA__` -> LoRA alpha (e.g. `8`)
- `__MAX_LENGTH__` -> max sequence length (e.g. `512`)
- `__BATCH_SIZE__` -> batch size (e.g. `4`)
- `__LEARNING_RATE__` -> learning rate (e.g. `2e-4`)
- `__NUM_EPOCHS__` -> number of training epochs (e.g. `3`)

Write the customized file to `.ml/train.py`.

### Step 2.6: Create Empty State Files

```bash
touch .ml/results.jsonl
touch .ml/experiments.jsonl
```

### Step 2.7: Compute Baselines

**If domain == "tabular":**

Run tabular baselines to establish the minimum bar:

```bash
cd .ml && python3 -c "
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

**If domain == "dl":**

For image_classification:

```bash
cd .ml && python3 -c "
import json, numpy as np
from pathlib import Path
from gsd_ml.baselines.deeplearning import compute_baselines

# Get labels from directory structure
data_dir = Path('{dataset_path}')
class_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])
labels = []
for i, d in enumerate(class_dirs):
    count = len(list(d.glob('*.*')))
    labels.extend([i] * count)
labels = np.array(labels)

baselines = compute_baselines(labels, '{metric}', 'image_classification')
print(json.dumps(baselines, default=str))
"
```

For text_classification:

```bash
cd .ml && python3 -c "
import json, numpy as np, pandas as pd
from pathlib import Path
from gsd_ml.baselines.deeplearning import compute_baselines

path = Path('{dataset_path}')
if path.suffix == '.json':
    df = pd.read_json(path)
else:
    df = pd.read_csv(path)

from sklearn.preprocessing import LabelEncoder
le = LabelEncoder()
labels = le.fit_transform(df['{target_column}'].values)
labels = np.array(labels)

baselines = compute_baselines(labels, '{metric}', 'text_classification')
print(json.dumps(baselines, default=str))
"
```

**If domain == "ft":**

```bash
cd .ml && python3 -c "
import json
from transformers import AutoTokenizer
from gsd_ml.baselines.finetuning import compute_baselines

tokenizer = AutoTokenizer.from_pretrained('{model_name}')
vocab_size = tokenizer.vocab_size
baselines = compute_baselines('{metric}', vocab_size)
print(json.dumps(baselines, default=str))
"
```

Persist baselines into config.json so they survive context resets:

```bash
python3 -c "
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

1. Get available families from config (domain-agnostic):

```bash
python3 -c "
from gsd_ml.drafts import get_families_for_domain
import json

config = json.loads(open('.ml/config.json').read())
draft_families = config.get('draft_families', [])
domain_map = {'tabular': 'tabular', 'dl': 'deeplearning', 'ft': 'finetuning'}
families = get_families_for_domain(domain_map[config['domain']])
selected = {k: v for k, v in families.items() if k in draft_families}
print(json.dumps(selected))
"
```

2. For each family:

   **If domain == "tabular":** (e.g., linear, random_forest, xgboost)
   - Edit `.ml/train.py` to use that family's model class (e.g., LogisticRegression for linear, RandomForestClassifier for random_forest, XGBClassifier for xgboost). Use default hyperparameters.

   **If domain == "dl":** (e.g., resnet, vit, efficientnet)
   - Edit `.ml/train.py` to change MODEL_NAME to the family's model. For image_classification: use the timm model name (e.g., `resnet50`, `vit_base_patch16_224`, `efficientnet_b0`). For text_classification: use the HuggingFace model name (e.g., `distilbert-base-uncased`, `bert-base-uncased`, `roberta-base`).

   **If domain == "ft":** (e.g., qlora_r8, qlora_r16, qlora_r32)
   - Edit `.ml/train.py` to change LORA_R and LORA_ALPHA to match the family configuration (e.g., r=8/alpha=8, r=16/alpha=16, r=32/alpha=32). For `lora_full`, also remove quantization config.

   Then for all domains:
   - Run `cd .ml && python3 train.py 2>.ml/train.log`
   - Parse the JSON metric from stdout
   - If the run succeeded, commit: `git add .ml/ && git commit -m "draft: {family} {metric}={value}"`
   - Record the commit hash and metric value
   - If the run failed (OOM, error), record metric_value=None

3. After all drafts complete, select the best:

```bash
python3 -c "
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
python3 -c "
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
- `consecutive_reverts` = 0
- `tried_families` = [] (or loaded from checkpoint if resuming)
- Read `start_time` from `.ml/config.json`

If resuming from a checkpoint, load `consecutive_reverts` and `tried_families` from checkpoint.json.

### Loop: Repeat Until Guardrails Trip

#### Step 3.1: Guardrail Check (Before Each Iteration)

Check all guardrails before starting each experiment:

1. **Experiment count:** Read `.ml/config.json` for `budget_experiments`. If `experiment_count >= budget_experiments`, STOP with message "Experiment budget exhausted ({experiment_count}/{budget_experiments})."

2. **Time budget:** Read `start_time` from `.ml/config.json`. Calculate elapsed seconds: `now - start_time`. If elapsed >= `budget_minutes * 60`, STOP with message "Time budget exhausted ({elapsed_minutes}/{budget_minutes} minutes)."

3. **Disk space:**
   ```bash
   python3 -c "import shutil; u=shutil.disk_usage('.'); print(u.free/(1024**3))"
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

**If domain == "tabular":**
- Try different model families: RandomForest, XGBoost, LightGBM, Ridge/LogisticRegression, GradientBoosting, ExtraTrees, SVM
- Try different hyperparameters: n_estimators, max_depth, learning_rate, regularization
- Try feature engineering: polynomial features, interaction terms, binning, feature selection
- Each iteration should be meaningfully different from previous attempts

**If domain == "dl":**
- Try different model architectures: for image try different timm models (resnet18/34/50/101, vit_small/base, efficientnet_b0-b4, convnext_tiny/small); for text try different HuggingFace models (distilbert, bert, roberta, albert)
- Try different learning rates: 1e-3, 5e-4, 1e-4, 3e-5
- Try different augmentation strategies (image): RandomCrop, ColorJitter, MixUp, CutMix
- Try different schedulers: CosineAnnealingLR, OneCycleLR, StepLR
- Try different batch sizes and image sizes

**If domain == "ft":**
- Try different LoRA configurations: r=8/16/32/64, alpha=8/16/32/64
- Try different learning rates: 2e-4, 1e-4, 5e-5, 3e-5
- Try different batch sizes: 1, 2, 4, 8 (with gradient accumulation)
- Try different number of epochs: 1, 2, 3, 5
- Try different max_length: 256, 512, 1024, 2048
- Try different target_modules: "all-linear", specific layer names

**IMPORTANT:** Only edit `.ml/train.py`. NEVER edit `.ml/prepare.py`.

#### Step 3.3: Run train.py

```bash
cd .ml && python3 train.py 2>.ml/train.log
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
python3 -c "
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

The `passes_baseline_gate` function has the same signature across all domains. Use the domain from config to select the correct import:

```bash
python3 -c "
import json, importlib
from pathlib import Path

config = json.loads(Path('.ml/config.json').read_text())
baselines = config.get('baselines', {})
domain = config['domain']

if not baselines:
    print('BASELINE_GATE_PASS')
else:
    module_map = {'tabular': 'tabular', 'dl': 'deeplearning', 'ft': 'finetuning'}
    mod = importlib.import_module(f'gsd_ml.baselines.{module_map[domain]}')
    if mod.passes_baseline_gate({metric_value}, baselines, '{direction}'):
        print('BASELINE_GATE_PASS')
    else:
        print('BASELINE_GATE_FAIL')
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
- Reset `consecutive_reverts = 0`

**If "revert":**
- Revert ONLY train.py:
  ```bash
  cd .ml && git checkout -- train.py
  ```
- **IMPORTANT:** Do NOT revert results.jsonl, experiments.jsonl, or checkpoint.json. These are append-only state files that must survive reverts.
- Increment `revert_count`
- Increment `consecutive_reverts += 1`

**If "retry":**
- The run failed due to OOM (Out of Memory)
- Edit train.py to reduce resource usage:
  - **If domain == "tabular":** Reduce n_estimators, max_depth, or batch_size. Use a simpler model. Reduce dataset size with sampling.
  - **If domain == "dl":** Reduce batch_size, use a smaller model (e.g. resnet18 instead of resnet50), reduce img_size, disable mixed precision.
  - **If domain == "ft":** Reduce batch_size, increase gradient_accumulation_steps, reduce max_length, reduce lora_r, use more aggressive quantization.
- Re-run train.py (go back to Step 3.3)
- Track retry count; DeviationHandler will return "stop" after 3 retries

**If "stop":**
- Repeated OOM failures; the system cannot handle this workload
- Print the reason and break the experiment loop
- This is a graceful stop, not an error

#### Step 3.5a: Run Diagnostics

After each experiment (regardless of keep/revert), if `.ml/predictions.csv` exists, run diagnostics:

**If domain == "ft" and metric in ("perplexity", "loss"):**

Skip diagnostics -- for FT with loss/perplexity metrics, predictions.csv contains per-sample losses (y_true=0.0, y_pred=loss_value) which are not meaningful for the diagnostics engine. Print: "Skipping diagnostics for FT loss/perplexity metric."

**Otherwise (tabular, DL, or FT with ROUGE metrics):**

```bash
python3 -c "
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
    if task in ('classification', 'image_classification', 'text_classification'):
        diag = diagnose_classification(preds['y_true'].values, preds['y_pred'].values)
    else:
        diag = diagnose_regression(preds['y_true'].values, preds['y_pred'].values)
    Path('.ml/diagnostics.json').write_text(json.dumps(diag, indent=2, default=str))
    print(json.dumps(diag, default=str))
"
```

Display the diagnostics summary. Note: `diagnostics.json` is ephemeral (overwritten each iteration), NOT saved in checkpoint.

#### Step 3.5b: Stagnation Check

After a revert, check if the session has stagnated (N consecutive reverts with no improvement). Skip this step if the last decision was "keep".

```bash
python3 -c "
import json
from gsd_ml.stagnation import check_stagnation
from gsd_ml.state import SessionState
from gsd_ml.drafts import get_families_for_domain

state = SessionState(
    consecutive_reverts={consecutive_reverts},
    tried_families={tried_families_list},
    best_commit='{best_commit}',
    best_metric={best_metric},
    run_id='{run_id}',
    task='{task}'
)

config = json.loads(open('.ml/config.json').read())
threshold = config.get('stagnation_threshold', 3)
domain = config.get('domain', 'tabular')

# Map domain to drafts domain name
drafts_domain = {'tabular': 'tabular', 'dl': 'deeplearning', 'ft': 'finetuning'}.get(domain, 'tabular')

if check_stagnation(state, threshold):
    families = get_families_for_domain(drafts_domain)
    untried = [f for f in families if f not in state.tried_families]
    if untried:
        print(json.dumps({'stagnated': True, 'new_family': untried[0], 'all_exhausted': False}))
    else:
        print(json.dumps({'stagnated': True, 'new_family': None, 'all_exhausted': True}))
else:
    print(json.dumps({'stagnated': False}))
"
```

Handle the result:

**If stagnated and new_family available:**

1. Print: "Stagnation detected ({consecutive_reverts} consecutive reverts). Branching to try {new_family}."
2. Save current state files to a temp location:
   ```bash
   cp .ml/results.jsonl /tmp/ml-stag-results.jsonl
   cp .ml/experiments.jsonl /tmp/ml-stag-experiments.jsonl
   cp .ml/checkpoint.json /tmp/ml-stag-checkpoint.json
   cp .ml/diagnostics.json /tmp/ml-stag-diagnostics.json 2>/dev/null || true
   ```
3. Create exploration branch:
   ```bash
   python3 -c "
   from gsd_ml.stagnation import trigger_stagnation_branch
   from gsd_ml.state import SessionState
   state = SessionState(best_commit='{best_commit}', consecutive_reverts={consecutive_reverts})
   branch = trigger_stagnation_branch('.', state, '{new_family}')
   print(branch)
   "
   ```
4. Restore saved state files back to `.ml/`:
   ```bash
   cp /tmp/ml-stag-results.jsonl .ml/results.jsonl
   cp /tmp/ml-stag-experiments.jsonl .ml/experiments.jsonl
   cp /tmp/ml-stag-checkpoint.json .ml/checkpoint.json
   cp /tmp/ml-stag-diagnostics.json .ml/diagnostics.json 2>/dev/null || true
   ```
5. Add `new_family` to `tried_families`
6. Reset `consecutive_reverts = 0`
7. Edit train.py to use the new model family
8. Continue the loop (next iteration will use the new family)

**If stagnated but all families exhausted:**

1. Print: "All model families exhausted. Continuing with current approach (trying hyperparameter variations)."
2. Reset `consecutive_reverts = 0` (give it another N tries)
3. Continue the loop

**If not stagnated:**

Continue to Step 3.5c (Record Results) -- no action needed.

#### Step 3.5c: Record Results

After each experiment (regardless of keep/revert decision), record:

**Append to results.jsonl:**

```bash
python3 -c "
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
python3 -c "
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
python3 -c "
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
    baselines=config.get('baselines'),
    consecutive_reverts={consecutive_reverts},
    tried_families={tried_families_list}
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
python3 -c "
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

**Domain-specific export notes:**
- **Tabular:** The artifact is the best sklearn/xgboost/lightgbm model (saved as pickle or joblib).
- **DL:** The artifact is `best_model.pt` (PyTorch state_dict). The export copies this to `artifacts/`.
- **FT:** The artifact is the `best_adapter/` directory (LoRA adapter weights + tokenizer config). The export copies this entire directory to `artifacts/`.

If no experiments succeeded (best_metric is None), skip export and note it in the retrospective.

### Step 4.2: Generate Retrospective

Calculate elapsed time: `duration_minutes = (now - start_time) / 60`

```bash
python3 -c "
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
Domain:       {domain}
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
   cd .ml && python3 train.py
   ```
   train.py uses paths relative to .ml/ (e.g. `../dataset.csv`).

4. **JSON output parsing** -- Parse the LAST line of stdout that contains valid JSON. Libraries (sklearn, xgboost, lightgbm) may print warnings or progress info before the JSON line.

5. **start_time persistence** -- Read `start_time` from `.ml/config.json` for guardrail checks. Do NOT rely on in-memory timers, which reset between context windows.

6. **CSV path** -- The CSV path in train.py and config.json is relative to the `.ml/` directory (typically `../dataset.csv`).

7. **Git branch** -- The branch `ml/run-{run_id}` must be created BEFORE the first experiment commit. All experiment commits go on this branch, never on main.

8. **State files** -- checkpoint.json, results.jsonl, and experiments.jsonl are the source of truth. They must be committed with keeps and never reverted.

9. **Stagnation state files** -- Before branching on stagnation, save results.jsonl, experiments.jsonl, checkpoint.json, and diagnostics.json. After creating the explore branch, restore these files. The explore branch starts from best-ever train.py but keeps the full experiment history.

10. **Domain routing** -- For DL/FT domains, the `domain` field in config.json determines which prepare module, template, and baseline module to use. The workflow reads this field to route correctly at every phase.
