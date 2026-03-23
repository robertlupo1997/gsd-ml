---
phase: 04-dl-fine-tuning
plan: 01
subsystem: ml-templates
tags: [pytorch, timm, transformers, peft, qlora, sfttrainer, mixed-precision]

requires:
  - phase: 01-python-port
    provides: "baselines/deeplearning.py and baselines/finetuning.py modules"
  - phase: 02-core-workflow-tabular
    provides: "train-tabular.py template pattern and metric-map.md"
provides:
  - "DL image classification training template (train-dl-image.py)"
  - "DL text classification training template (train-dl-text.py)"
  - "Fine-tuning training template with QLoRA (train-ft.py)"
  - "passes_baseline_gate() in DL and FT baseline modules"
  - "Metric map extended with DL and FT metrics"
affects: [04-02-PLAN, workflows]

tech-stack:
  added: [timm, transformers, peft, trl, bitsandbytes]
  patterns: [__PLACEHOLDER__ constants, de-Jinja2 templates, processing_class over tokenizer]

key-files:
  created:
    - gsd-ml/templates/train-dl-image.py
    - gsd-ml/templates/train-dl-text.py
    - gsd-ml/templates/train-ft.py
    - python/tests/test_templates.py
  modified:
    - python/src/gsd_ml/baselines/deeplearning.py
    - python/src/gsd_ml/baselines/finetuning.py
    - gsd-ml/references/metric-map.md
    - python/tests/test_baselines.py

key-decisions:
  - "Used processing_class=tokenizer instead of deprecated tokenizer= param in SFTTrainer"
  - "Split DL into separate image and text templates (not one with conditionals)"
  - "Removed DATASET_FORMAT constant from FT template (not needed with static template)"

patterns-established:
  - "DL templates follow same docstring/JSON-output pattern as tabular template"
  - "All baseline modules export both compute_baselines() and passes_baseline_gate()"

requirements-completed: [DL-01, DL-02, DL-03, DL-04, FT-01, FT-02, FT-03, FT-04]

duration: 3min
completed: 2026-03-23
---

# Phase 4 Plan 1: DL/FT Building Blocks Summary

**Three static training templates (DL image, DL text, FT with QLoRA), baseline gates, and extended metric map covering all three ML domains**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-23T00:57:19Z
- **Completed:** 2026-03-23T01:00:30Z
- **Tasks:** 2 (TDD: tests first, then implementation)
- **Files modified:** 8

## Accomplishments
- Created 3 de-Jinja2'd training templates with __PLACEHOLDER__ constants and no conditional logic
- Added passes_baseline_gate() to both DL and FT baseline modules (identical to tabular pattern)
- Extended metric-map.md with DL metrics (accuracy, f1_weighted, loss) and FT metrics (perplexity, loss, rouge1, rougeL)
- All 188 tests pass including 15 new template content tests and 11 new baseline tests

## Task Commits

Each task was committed atomically:

1. **Task 2 (TDD RED): Tests** - `1d16021` (test)
2. **Task 1 (TDD GREEN): Implementation** - `4b23c57` (feat)

_TDD flow: tests written first, verified failing, then implementation made them pass._

## Files Created/Modified
- `gsd-ml/templates/train-dl-image.py` - Image classification with timm, mixed precision, early stopping
- `gsd-ml/templates/train-dl-text.py` - Text classification with AutoModelForSequenceClassification, dict batch handling
- `gsd-ml/templates/train-ft.py` - QLoRA fine-tuning with SFTTrainer, evaluate_perplexity(), evaluate_rouge()
- `python/src/gsd_ml/baselines/deeplearning.py` - Added passes_baseline_gate()
- `python/src/gsd_ml/baselines/finetuning.py` - Added passes_baseline_gate()
- `gsd-ml/references/metric-map.md` - Added DL and FT metric sections
- `python/tests/test_templates.py` - 15 template content validation tests
- `python/tests/test_baselines.py` - Added TestDLBaselines and TestFTBaselines classes

## Decisions Made
- Used `processing_class=tokenizer` instead of deprecated `tokenizer=` param in SFTTrainer per research recommendation
- Split DL template into separate image and text files rather than keeping Jinja2 conditionals
- Removed `DATASET_FORMAT` constant from FT template since static templates don't need format routing

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All DL/FT building blocks ready for Plan 02 (workflow integration)
- Templates follow same pattern as tabular (scaffold phase replaces __PLACEHOLDER__ constants)
- Baseline gates available for both DL and FT experiment loops

---
*Phase: 04-dl-fine-tuning*
*Completed: 2026-03-23*
