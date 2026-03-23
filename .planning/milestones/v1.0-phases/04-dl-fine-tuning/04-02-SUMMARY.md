---
phase: 04-dl-fine-tuning
plan: 02
subsystem: workflow
tags: [domain-routing, deep-learning, fine-tuning, ml-run, workflow]

requires:
  - phase: 04-dl-fine-tuning/01
    provides: DL and FT templates (train-dl-image.py, train-dl-text.py, train-ft.py) and Python modules (prepare, baselines)
provides:
  - Multi-domain ml-run.md workflow with tabular, DL, and FT routing
  - Domain-conditional profiling, scaffolding, baselines, loop, and finalize phases
affects: [05-safety-ux, 06-polish]

tech-stack:
  added: []
  patterns: [domain-conditional workflow branching with inline "If domain == X" sections]

key-files:
  created: []
  modified: [gsd-ml/workflows/ml-run.md]

key-decisions:
  - "Inline domain conditionals in single workflow file rather than separate per-domain workflows"
  - "DL image profiling counts subdirectory structure, text profiling reads CSV/JSON for label distribution"
  - "FT skips profiling entirely, sets task=sft and metric=perplexity by default"
  - "Skip diagnostics for FT with loss/perplexity metrics (per-sample losses not meaningful for diagnostics engine)"
  - "Map domain names to drafts domain names: dl->deeplearning, ft->finetuning for stagnation family lookup"

patterns-established:
  - "Domain routing pattern: read config.json domain field to select prepare module, template, and baseline module"
  - "GPU warning pattern: check get_device_info early for DL/FT, warn but do not block"

requirements-completed: [DL-01, DL-02, DL-03, DL-04, FT-01, FT-02, FT-03, FT-04]

duration: 4min
completed: 2026-03-23
---

# Phase 04 Plan 02: DL/FT Domain Routing Summary

**Multi-domain workflow routing in ml-run.md for tabular, DL (image/text classification), and FT (LoRA/QLoRA fine-tuning) experiment paths**

## Performance

- **Duration:** 4 min
- **Started:** 2026-03-23T01:03:13Z
- **Completed:** 2026-03-23T01:07:30Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Extended ml-run.md with domain-conditional branches at all 4 phases (profile, scaffold, loop, finalize)
- DL routing: image classification (directory-based profiling, timm models) and text classification (CSV/JSON profiling, HuggingFace models)
- FT routing: skip profiling, LoRA config scaffolding, vocab-based baselines, best_adapter/ export
- GPU warning surfaced early for DL/FT via get_device_info check
- Existing tabular path completely unchanged

## Task Commits

Each task was committed atomically:

1. **Task 1: Add DL and FT domain routing to ml-run.md workflow** - `5c31f8a` (feat)

**Plan metadata:** pending (docs: complete plan)

## Files Created/Modified
- `gsd-ml/workflows/ml-run.md` - Extended with domain routing for DL and FT at every workflow phase

## Decisions Made
- Kept all routing inline in a single workflow file using "If domain == X" conditional sections, as recommended by the research phase
- DL image classification profiling counts subdirectory structure (one dir per class), sets metric=accuracy
- DL text classification profiling reads CSV/JSON to detect num_labels, sets metric=f1_weighted
- FT skips profiling entirely -- sets task=sft, default metric=perplexity, direction=minimize
- Skip diagnostics for FT with loss/perplexity metrics since per-sample loss values are not meaningful for the diagnostics engine
- Domain name mapping for drafts: dl->deeplearning, ft->finetuning (matching ALGORITHM_FAMILIES keys in drafts.py)

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ml-run.md now handles all 3 domains end-to-end
- Phase 04 complete -- ready for Phase 05 (Safety and UX)

---
*Phase: 04-dl-fine-tuning*
*Completed: 2026-03-23*
