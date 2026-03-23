# Phase 4: DL + Fine-Tuning - Research

**Researched:** 2026-03-22
**Domain:** Deep learning (PyTorch/timm/transformers) and LLM fine-tuning (peft/trl/bitsandbytes)
**Confidence:** HIGH

## Summary

Phase 4 extends gsd-ml from tabular-only to deep learning (image classification, text classification) and LLM fine-tuning (LoRA/QLoRA). The heavy lifting is already done: all Python utilities (prepare/deeplearning.py, prepare/finetuning.py, baselines/deeplearning.py, baselines/finetuning.py) were ported in Phase 1 and the drafts.py module already has DL and FT algorithm families defined. The workflow (ml-run.md) already handles the core loop -- what remains is adding domain routing (DL/FT branches in the workflow), creating two new static training templates (train-dl.py, train-ft.py), a DL+FT metric reference, and adding `passes_baseline_gate` to the DL/FT baseline modules.

**Primary recommendation:** Follow the exact same pattern as Phase 2 -- create static templates with `__PLACEHOLDER__` constants, add domain-conditional branches to ml-run.md, and add the metric-map reference for DL/FT metrics. Do NOT restructure the existing workflow.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| DL-01 | PyTorch + timm for image classification | Template train-dl.py with image_classification task, prepare/deeplearning.py already has load_image_data() |
| DL-02 | PyTorch + transformers for text classification | Template train-dl.py with text_classification task, prepare/deeplearning.py already has load_text_data() |
| DL-03 | GPU-aware training templates | prepare/deeplearning.py has get_device_info(), train-dl.py uses torch.amp.autocast + GradScaler |
| DL-04 | DL-specific baselines (random, most_frequent) | baselines/deeplearning.py already implements compute_baselines(), needs passes_baseline_gate() |
| FT-01 | LoRA/QLoRA via peft and trl | Template train-ft.py uses BitsAndBytesConfig, LoraConfig, SFTTrainer |
| FT-02 | HuggingFace model loading and adapter training | train-ft.py loads AutoModelForCausalLM with quantization, applies get_peft_model() |
| FT-03 | Metrics: perplexity, rouge1, rougeL, loss | train-ft.py has evaluate_perplexity() and evaluate_rouge(), metric-map needs FT entries |
| FT-04 | FT-specific baselines (random, base_model) | baselines/finetuning.py already implements compute_baselines(), needs passes_baseline_gate() |
</phase_requirements>

## Standard Stack

### Core (already installed in gsd_ml)
| Library | Purpose | Why Standard |
|---------|---------|--------------|
| torch | DL framework, GPU compute | Universal DL backend |
| torchvision | Image transforms, ImageFolder | Standard image pipeline |
| timm | Pretrained image models (ResNet, ViT, EfficientNet) | 800+ models, single API |
| transformers | HF model hub, tokenizers, AutoModel* | Industry standard for NLP/LLM |
| peft | LoRA/QLoRA adapter layer | Official HF parameter-efficient FT |
| trl | SFTTrainer for instruction tuning | Official HF trainer for SFT/RLHF |
| bitsandbytes | 4-bit/8-bit quantization | Required for QLoRA |
| evaluate | HF metrics (ROUGE, etc.) | Official HF evaluation library |

### Supporting (already in gsd_ml)
| Library | Purpose | When to Use |
|---------|---------|-------------|
| sklearn (DummyClassifier) | DL baselines | Used by baselines/deeplearning.py |
| pandas | Predictions CSV | Save predictions for diagnostics |
| numpy | Label arrays for baselines | Baseline computation |

### No New Dependencies Required
All libraries above are already declared in the gsd_ml Python package from Phase 1 porting. No new pip dependencies need to be added.

## Architecture Patterns

### What Already Exists (from Phase 1 + Phase 2)

The following are already ported and working:

```
python/src/gsd_ml/
  prepare/
    deeplearning.py    # get_device_info(), load_image_data(), load_text_data()
    finetuning.py      # get_vram_info(), format_dataset(), create_train_eval_split()
  baselines/
    deeplearning.py    # compute_baselines(labels, scoring, task)
    finetuning.py      # compute_baselines(metric, vocab_size)
  drafts.py            # ALGORITHM_FAMILIES["deeplearning"], ALGORITHM_FAMILIES["finetuning"]
```

### What Needs to Be Created

```
gsd-ml/templates/
  train-dl.py          # Static template (de-Jinja2 from dl_train.py.j2)
  train-ft.py          # Static template (de-Jinja2 from ft_train.py.j2)

gsd-ml/references/
  metric-map.md        # Add DL + FT metrics section (or create metric-map-dl.md / metric-map-ft.md)

gsd-ml/workflows/
  ml-run.md            # Add domain routing branches for dl and ft
```

### Pattern: Static Template with Placeholders (same as tabular)

The mlforge templates use Jinja2 (`{{ variable }}`). Phase 2 converted the tabular template to use `__PLACEHOLDER__` constants. Apply the same pattern to DL and FT:

**DL template placeholders:**
- `__TASK__` -- "image_classification" or "text_classification"
- `__METRIC__` -- "accuracy", "f1_weighted", "loss"
- `__DATA_PATH__` -- path to data directory or file
- `__MODEL_NAME__` -- timm model name or HF model name
- `__IMG_SIZE__` -- image resize dimension (default 224)
- `__BATCH_SIZE__` -- batch size (default 32 for image, 16 for text)
- `__TIME_BUDGET_SEC__` -- time budget in seconds

**FT template placeholders:**
- `__MODEL_NAME__` -- HuggingFace model name (e.g. "meta-llama/Llama-3-8B")
- `__METRIC__` -- "perplexity", "loss", "rouge1", "rougeL"
- `__LORA_R__` -- LoRA rank (default 8)
- `__LORA_ALPHA__` -- LoRA alpha (default 8)
- `__MAX_LENGTH__` -- max sequence length (default 512)
- `__BATCH_SIZE__` -- batch size (default 2)
- `__LEARNING_RATE__` -- learning rate (default 2e-4)
- `__NUM_EPOCHS__` -- number of epochs (default 3)
- `__DATASET_FORMAT__` -- "instruction" (default)

### Pattern: Domain Routing in ml-run.md

The workflow needs conditional branches at key points:

1. **Phase 1 (Profile):** DL/FT skip the CSV profiler. DL validates directory structure (ImageFolder) or CSV/JSON for text. FT validates JSONL/JSON/CSV with instruction/output columns.

2. **Phase 2 (Scaffold):** Domain-specific prepare.py, train.py template, config.json fields, and baseline computation differ by domain.

3. **Phase 3 (Loop):** The loop structure is identical -- only the train.py content differs, which Claude Code edits. The diagnostics for DL/FT may not produce predictions.csv in all cases (FT loss-based metrics save per-sample losses instead).

4. **Phase 4 (Finalize):** Export differs -- DL saves best_model.pt, FT saves adapter directory. The retrospective and tagging work the same.

### Anti-Patterns to Avoid
- **Separate workflow files per domain:** Do NOT create ml-run-dl.md and ml-run-ft.md. The workflow structure is 95% identical. Use inline conditionals (`if domain == "dl"`) in the relevant steps.
- **Jinja2 templates:** Do NOT use Jinja2. Use `__PLACEHOLDER__` constants that the workflow replaces with sed or Python string replacement.
- **Breaking the DL template into image vs text sub-templates:** The mlforge template handled both via Jinja2 conditionals. The static template should include BOTH paths with clear comments, and Claude Code selects the right one during the draft/edit phase.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Image data loading | Custom PIL loop | `torchvision.datasets.ImageFolder` via prepare/deeplearning.py | Handles train/val split, transforms, normalization |
| Text tokenization | Custom tokenizer | `transformers.AutoTokenizer` via prepare/deeplearning.py | Handles padding, truncation, special tokens |
| QLoRA setup | Manual quantization code | `BitsAndBytesConfig` + `LoraConfig` + `get_peft_model` | Correct NF4 quantization, double quant |
| SFT training | Custom training loop | `trl.SFTTrainer` | Handles gradient accumulation, eval, logging |
| ROUGE evaluation | Custom string matching | `evaluate.load("rouge")` | Standard ROUGE implementation |
| Mixed precision | Manual dtype casting | `torch.amp.autocast` + `GradScaler` | Handles loss scaling, gradient clipping |
| GPU detection | nvidia-smi parsing | `torch.cuda.is_available()` + `torch.cuda.get_device_name()` | Already in prepare modules |
| Chat formatting | Manual prompt templates | `tokenizer.apply_chat_template()` | Already in prepare/finetuning.py |

## Common Pitfalls

### Pitfall 1: DL Template Task Branching
**What goes wrong:** The mlforge DL template used Jinja2 `{% if task == "image_classification" %}` to conditionally include imports and code. A static template cannot do this.
**Why it happens:** Image classification imports timm, text classification imports transformers -- different imports for different tasks.
**How to avoid:** Include BOTH paths in the static template, clearly commented. The workflow tells Claude Code which task type to use, and Claude Code removes/modifies the unused path during its first edit. Alternatively, use two separate templates (train-dl-image.py, train-dl-text.py) -- this is simpler.
**Recommendation:** Use two separate DL templates. The tabular domain only has one task type, but DL has fundamentally different imports/models for image vs text. Two templates is cleaner than one template with dead code.

### Pitfall 2: FT Baseline Gate Direction
**What goes wrong:** For FT metrics like perplexity and loss, lower is better. The baseline gate must use direction="minimize" correctly.
**Why it happens:** The tabular baseline gate was built for maximize-first metrics. FT baselines (random_guess loss = log(vocab_size)) are upper bounds -- model must score BELOW them.
**How to avoid:** The `passes_baseline_gate` function already handles direction correctly in tabular.py. Add the same function to baselines/deeplearning.py and baselines/finetuning.py. For FT, perplexity direction="minimize" and loss direction="minimize".

### Pitfall 3: DL Profiler Step
**What goes wrong:** The workflow calls `profiler.profile_dataset()` which expects a pandas DataFrame with a target column. DL image data is a directory of images, not a CSV.
**Why it happens:** The profiler was built for tabular data.
**How to avoid:** For DL image classification, skip the pandas profiler. Instead, count classes from subdirectory names, count images, and set task/metric directly. For DL text classification, the profiler CAN work if the data is CSV/JSON with text+label columns. For FT, skip profiling entirely -- the task is always "sft" and the metric is user-specified or defaults to "perplexity".

### Pitfall 4: FT Data Path Convention
**What goes wrong:** Tabular uses CSV_PATH relative to .ml/ (e.g., `../dataset.csv`). FT data might be JSONL, JSON, or CSV.
**Why it happens:** The prepare/finetuning.py `_load_data()` handles all three formats, but the template hardcodes `data_path="data.json"`.
**How to avoid:** The FT template should use a `__DATA_PATH__` placeholder, and the workflow should set it to the relative path to the actual data file.

### Pitfall 5: GPU Requirement for DL/FT
**What goes wrong:** DL and FT are impractical without a GPU. Running on CPU wastes time budget.
**Why it happens:** The prepare modules detect CPU and still proceed.
**How to avoid:** The workflow should check `get_device_info()` or `get_vram_info()` early and warn the user if no GPU is detected. For FT, recommend_quantization=True when VRAM < 16GB is already handled. The workflow should NOT block on CPU (user may have a reason), but should prominently warn.

### Pitfall 6: DL Baselines Need Labels Array
**What goes wrong:** `baselines/deeplearning.py.compute_baselines()` takes a `labels` numpy array. For image data, you need to extract labels from the ImageFolder dataset.
**Why it happens:** ImageFolder stores labels as indices in `.targets`.
**How to avoid:** The workflow baseline step for DL should: (1) use `torchvision.datasets.ImageFolder` to get `.targets`, (2) pass that array to `compute_baselines()`. Or simpler: count classes and compute theoretical baselines without loading data (similar to FT approach). Actually, the existing DL baselines already work with just a labels array and sklearn DummyClassifier -- no torch needed.

### Pitfall 7: SFTTrainer API Changes
**What goes wrong:** The `tokenizer` parameter in SFTTrainer was deprecated in recent trl versions in favor of `processing_class`.
**Why it happens:** trl API evolved.
**How to avoid:** Use `processing_class=tokenizer` instead of `tokenizer=tokenizer` in the FT template. Flag as MEDIUM confidence -- verify against installed trl version at runtime. The template should try the newer API first.

## Code Examples

### DL Template Structure (image classification)
```python
# Source: mlforge/templates/dl_train.py.j2 (de-Jinja2'd)
"""Mutable train.py for deep learning experiments."""
import json, time, torch, torch.nn as nn, torch.optim as optim
from torch.optim.lr_scheduler import ReduceLROnPlateau
import timm
from prepare import get_device_info, load_image_data

DATA_DIR = "__DATA_PATH__"
IMG_SIZE = __IMG_SIZE__
BATCH_SIZE = __BATCH_SIZE__
MODEL_NAME = "__MODEL_NAME__"
METRIC_NAME = "__METRIC__"
TIME_BUDGET_SEC = __TIME_BUDGET_SEC__

def train():
    device_info = get_device_info()
    device = torch.device(device_info["device"])
    train_loader, val_loader, num_classes = load_image_data(DATA_DIR, img_size=IMG_SIZE, batch_size=BATCH_SIZE)
    model = timm.create_model(MODEL_NAME, pretrained=True, num_classes=num_classes).to(device)
    # ... training loop with early stopping, mixed precision, gradient clipping
    # ... save predictions.csv and best_model.pt
    print(json.dumps({"metric_value": best_metric, "metric_name": METRIC_NAME}))
```

### FT Template Structure
```python
# Source: mlforge/templates/ft_train.py.j2 (de-Jinja2'd)
"""Mutable train.py for fine-tuning experiments."""
import json, math, torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments
from peft import LoraConfig, TaskType, get_peft_model
from trl import SFTTrainer
from prepare import format_dataset, get_vram_info

MODEL_NAME = "__MODEL_NAME__"
LORA_R = __LORA_R__
LORA_ALPHA = __LORA_ALPHA__
METRIC = "__METRIC__"
MAX_LENGTH = __MAX_LENGTH__
BATCH_SIZE = __BATCH_SIZE__

def main():
    quant_config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, quantization_config=quant_config, device_map="auto")
    # ... LoRA config, dataset loading, SFTTrainer, evaluation
    print(json.dumps({"metric_value": eval_metric, "metric_name": METRIC}))
```

### Baseline Gate for DL/FT (needs to be added)
```python
# Add to baselines/deeplearning.py and baselines/finetuning.py
def passes_baseline_gate(metric_value, baselines, direction):
    for baseline_info in baselines.values():
        baseline_score = baseline_info["score"]
        if direction == "maximize" and metric_value <= baseline_score:
            return False
        if direction == "minimize" and metric_value >= baseline_score:
            return False
    return True
```

### Workflow Domain Routing Example
```markdown
### Step 1.3: Profile the Dataset

**If domain == "tabular":** [existing profiler code]

**If domain == "dl" and task == "image_classification":**
```bash
python -c "
import json
from pathlib import Path
data_dir = Path('{dataset_path}')
classes = sorted([d.name for d in data_dir.iterdir() if d.is_dir() and d.name not in ('train', 'val')])
# ... count images, detect train/val split
print(json.dumps({'task': 'image_classification', 'num_classes': len(classes), 'metric': 'accuracy', 'direction': 'maximize'}))
"
```

**If domain == "ft":**
Skip profiling. Set task="sft", metric defaults to "perplexity", direction="minimize".
```

## State of the Art

| Old Approach (mlforge) | Current Approach (gsd-ml) | Impact |
|------------------------|---------------------------|--------|
| Jinja2 templates with `{{ var }}` | Static .py with `__PLACEHOLDER__` constants | No Jinja2 dependency, Claude Code edits directly |
| GitPython for branching | subprocess git calls | Already handled in Phase 1 |
| Config dataclass | JSON config dict | Already handled in Phase 1 |
| SFTTrainer(tokenizer=...) | SFTTrainer(processing_class=...) | trl API update, verify at runtime |

**Key version notes:**
- timm: Use whatever is installed; the template uses `timm.create_model()` API which is stable across versions
- transformers: `AutoModelForCausalLM.from_pretrained()` API is stable
- peft: `get_peft_model()` API is stable; `LoraConfig(target_modules="all-linear")` works in recent versions
- trl: `SFTTrainer` API has evolved; the `tokenizer` parameter may need to be `processing_class`
- bitsandbytes: `BitsAndBytesConfig` API is stable

## Open Questions

1. **DL template: one or two files?**
   - What we know: Image classification uses timm, text classification uses transformers -- fundamentally different imports
   - What's unclear: Whether having dead code paths in a single template confuses Claude Code during editing
   - Recommendation: Use two separate templates (train-dl-image.py, train-dl-text.py). Cleaner for Claude Code to iterate on.

2. **SFTTrainer API parameter name**
   - What we know: Recent trl versions deprecated `tokenizer=` in favor of `processing_class=`
   - What's unclear: Which version is installed in the user's environment
   - Recommendation: Use `processing_class=tokenizer` in the template. If it fails, Claude Code will see the deprecation warning and fix it during iteration.

3. **FT model download during experiment**
   - What we know: First FT run downloads multi-GB model files from HuggingFace Hub
   - What's unclear: Whether this should count against time budget
   - Recommendation: Accept it -- the model download happens once and is cached. The time budget is generous enough for this.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | python/pyproject.toml |
| Quick run command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` |
| Full suite command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DL-01 | timm image classification template exists and has correct placeholders | unit | `pytest python/tests/test_templates.py::test_dl_image_template -x` | No - Wave 0 |
| DL-02 | transformers text classification template exists and has correct placeholders | unit | `pytest python/tests/test_templates.py::test_dl_text_template -x` | No - Wave 0 |
| DL-03 | get_device_info returns GPU info or CPU fallback | unit | `pytest python/tests/test_prepare_dl.py::test_get_device_info -x` | No - Wave 0 |
| DL-04 | DL baselines compute and baseline gate works | unit | `pytest python/tests/test_baselines.py::TestDLBaselines -x` | No - Wave 0 |
| FT-01 | FT template has QLoRA config placeholders | unit | `pytest python/tests/test_templates.py::test_ft_template -x` | No - Wave 0 |
| FT-02 | FT template loads model with quantization | unit | `pytest python/tests/test_templates.py::test_ft_model_loading -x` | No - Wave 0 |
| FT-03 | FT metric map includes perplexity, rouge1, rougeL, loss | unit | `pytest python/tests/test_templates.py::test_ft_metrics -x` | No - Wave 0 |
| FT-04 | FT baselines compute and baseline gate works | unit | `pytest python/tests/test_baselines.py::TestFTBaselines -x` | No - Wave 0 |

### Sampling Rate
- **Per task commit:** `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q`
- **Per wave merge:** `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `python/tests/test_baselines.py` -- add TestDLBaselines and TestFTBaselines classes (DL-04, FT-04)
- [ ] `python/tests/test_templates.py` -- new file to verify template content (DL-01, DL-02, FT-01, FT-02, FT-03)
- [ ] Template files and workflow updates are the primary deliverables, tested by template content verification

## Sources

### Primary (HIGH confidence)
- Existing codebase: `python/src/gsd_ml/baselines/deeplearning.py` -- DL baseline implementation
- Existing codebase: `python/src/gsd_ml/baselines/finetuning.py` -- FT baseline implementation
- Existing codebase: `python/src/gsd_ml/prepare/deeplearning.py` -- DL data pipeline
- Existing codebase: `python/src/gsd_ml/prepare/finetuning.py` -- FT data pipeline
- Existing codebase: `python/src/gsd_ml/drafts.py` -- DL and FT algorithm families
- Source template: `/home/tlupo/AutoML/src/mlforge/templates/dl_train.py.j2` -- original DL template
- Source template: `/home/tlupo/AutoML/src/mlforge/templates/ft_train.py.j2` -- original FT template
- Existing workflow: `gsd-ml/workflows/ml-run.md` -- tabular workflow to extend
- Existing template: `gsd-ml/templates/train-tabular.py` -- pattern for static templates

### Secondary (MEDIUM confidence)
- trl SFTTrainer API changes -- `processing_class` vs `tokenizer` parameter

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH -- all libraries already ported, just need templates and workflow
- Architecture: HIGH -- follows exact same pattern as tabular (Phase 2)
- Pitfalls: HIGH -- most pitfalls are visible from reading existing code and mlforge templates

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- core APIs are mature)
