---
phase: 02-core-workflow-tabular
plan: 01
subsystem: ml-workflow
tags: [sklearn, xgboost, lightgbm, tabular, template, metrics]

requires:
  - phase: 01-package-skeleton
    provides: npm install.js that copies gsd-ml/ directory recursively
provides:
  - Static train-tabular.py template for tabular ML experiments
  - Metric-map.md reference for metric interpretation
  - Updated skill file with argument parsing and references
affects: [02-core-workflow-tabular, ml-run workflow]

tech-stack:
  added: []
  patterns: [static-template-with-placeholders, metric-reference-map]

key-files:
  created:
    - gsd-ml/templates/train-tabular.py
    - gsd-ml/references/metric-map.md
  modified:
    - commands/gsd-ml/ml.md

key-decisions:
  - "Removed Optuna entirely -- Claude Code iterates manually via edit/run/keep/revert cycle"
  - "Unified classification and regression in single template with TASK constant"
  - "Used placeholder constants (__CSV_PATH__ etc) instead of Jinja2 variables"

patterns-established:
  - "Static template pattern: Python file with __PLACEHOLDER__ constants that scaffold phase fills in"
  - "Reference document pattern: markdown tables mapping domain concepts to implementation details"

requirements-completed: [SCAF-03, TAB-01, TAB-02, TAB-03, PROF-02]

duration: 2min
completed: 2026-03-22
---

# Phase 2 Plan 1: Template and Reference Files Summary

**Static train-tabular.py template (de-Jinja2'd from mlforge) with sklearn/XGBoost/LightGBM support, cross-validation via prepare.evaluate(), and metric-map.md reference covering 6 tabular metrics**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T23:49:01Z
- **Completed:** 2026-03-22T23:51:01Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- Created static train-tabular.py template that compiles as valid Python, with both classification and regression models, try/except for xgboost/lightgbm, and JSON stdout output contract
- Created metric-map.md reference documenting all 6 tabular metrics with sklearn scoring strings, task types, and optimization direction
- Updated skill file to parse dataset/target arguments and reference both workflow and metric-map

## Task Commits

Each task was committed atomically:

1. **Task 1: Create static train-tabular.py template and metric-map.md reference** - `dfd13b4` (feat)
2. **Task 2: Update skill file with proper argument parsing** - `6dc43b9` (feat)

## Files Created/Modified
- `gsd-ml/templates/train-tabular.py` - Static starter train.py for tabular ML experiments (de-Jinja2'd from mlforge)
- `gsd-ml/references/metric-map.md` - Metric name to sklearn scoring string mapping with direction notes
- `commands/gsd-ml/ml.md` - Updated skill entry point with argument parsing and metric-map reference

## Decisions Made
- Removed Optuna entirely: Claude Code iterates manually via edit/run/keep/revert cycle, no HPO framework needed
- Unified classification and regression in single template: TASK constant determines which model class is used
- Used __PLACEHOLDER__ constants instead of Jinja2 variables: scaffold phase does simple string replacement

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Template and reference files ready for the ml-run.md workflow (Plan 02) to reference
- Skill file properly wired to workflow and metric-map reference
- All 162 existing tests still pass

---
*Phase: 02-core-workflow-tabular*
*Completed: 2026-03-22*
