---
phase: 01-foundation
plan: 01
subsystem: python-utilities
tags: [python, pip, scikit-learn, pandas, numpy, xgboost, lightgbm]

# Dependency graph
requires: []
provides:
  - "pip-installable gsd_ml package with 17 modules"
  - "Complete test suite (162 tests)"
  - "Tabular, DL, and fine-tuning baselines/prepare subpackages"
affects: [02-npm-package, 03-skills, 04-workflows]

# Tech tracking
tech-stack:
  added: [hatchling, scikit-learn, pandas, numpy, xgboost, lightgbm, pyarrow, pytest]
  patterns: [lazy-imports-for-optional-deps, dict-config-over-dataclass, subprocess-over-gitpython]

key-files:
  created:
    - python/pyproject.toml
    - python/src/gsd_ml/__init__.py
    - python/src/gsd_ml/state.py
    - python/src/gsd_ml/checkpoint.py
    - python/src/gsd_ml/profiler.py
    - python/src/gsd_ml/guardrails.py
    - python/src/gsd_ml/results.py
    - python/src/gsd_ml/journal.py
    - python/src/gsd_ml/diagnostics.py
    - python/src/gsd_ml/drafts.py
    - python/src/gsd_ml/stagnation.py
    - python/src/gsd_ml/retrospective.py
    - python/src/gsd_ml/export.py
    - python/src/gsd_ml/baselines/tabular.py
    - python/src/gsd_ml/baselines/deeplearning.py
    - python/src/gsd_ml/baselines/finetuning.py
    - python/src/gsd_ml/prepare/tabular.py
    - python/src/gsd_ml/prepare/deeplearning.py
    - python/src/gsd_ml/prepare/finetuning.py
  modified: []

key-decisions:
  - "Used dict config instead of Config dataclass for guardrails/retrospective/export -- simpler, no TOML dependency"
  - "Replaced GitPython with subprocess.run for journal.py and stagnation.py -- eliminates heavy dependency"
  - "Lazy-imported torch in prepare/deeplearning.py so module imports without DL deps installed"
  - "Lazy-imported validate_no_leakage in profiler.py to avoid import-time circular dependency"

patterns-established:
  - "Lazy imports: optional heavy dependencies (torch, transformers) imported inside functions, not at module level"
  - "Dict config: all config passed as plain dicts with .get() defaults instead of dataclass attributes"
  - "Subprocess git: all git operations use subprocess.run instead of GitPython library"

requirements-completed: [PKG-03]

# Metrics
duration: 12min
completed: 2026-03-22
---

# Phase 1 Plan 1: Python Package Port Summary

**Pip-installable gsd_ml package with all 17 mlforge modules ported, 3 adapted (guardrails/journal/stagnation), and 162 tests passing**

## Performance

- **Duration:** 12 min
- **Started:** 2026-03-22T18:55:22Z
- **Completed:** 2026-03-22T19:07:04Z
- **Tasks:** 2
- **Files modified:** 36

## Accomplishments
- Ported all 17 Python modules from mlforge to gsd_ml with correct imports
- Adapted 3 modules: guardrails (dict config), journal (subprocess git), stagnation (subprocess git)
- Created comprehensive test suite with 162 passing tests
- Zero references to mlforge or GitPython remain in source

## Task Commits

Each task was committed atomically:

1. **Task 1: Create Python package and port all 17 modules** - `5c0fa3d` (feat)
2. **Task 2: Port test suite and make it pass** - `11c6bb1` (test)

## Files Created/Modified
- `python/pyproject.toml` - Package build config (hatchling, deps)
- `python/src/gsd_ml/__init__.py` - Package root with __version__
- `python/src/gsd_ml/state.py` - SessionState dataclass
- `python/src/gsd_ml/checkpoint.py` - Checkpoint save/load with schema versioning
- `python/src/gsd_ml/profiler.py` - Dataset profiling and auto-detection
- `python/src/gsd_ml/guardrails.py` - Resource guardrails with dict config
- `python/src/gsd_ml/results.py` - JSONL experiment results tracker
- `python/src/gsd_ml/journal.py` - Experiment journal with subprocess git
- `python/src/gsd_ml/diagnostics.py` - Regression/classification error analysis
- `python/src/gsd_ml/drafts.py` - Multi-draft generation and selection
- `python/src/gsd_ml/stagnation.py` - Branch-on-stagnation with subprocess git
- `python/src/gsd_ml/retrospective.py` - Run retrospective report generation
- `python/src/gsd_ml/export.py` - Artifact export with metadata sidecar
- `python/src/gsd_ml/baselines/*.py` - Baseline computation (tabular, DL, FT)
- `python/src/gsd_ml/prepare/*.py` - Data pipelines (tabular, DL, FT)
- `python/tests/*.py` - 14 test files with 162 tests

## Decisions Made
- Used dict config instead of Config dataclass for guardrails/retrospective/export -- eliminates TOML parsing dependency
- Replaced GitPython with subprocess.run for journal.py and stagnation.py -- removes heavy dependency
- Lazy-imported torch in prepare/deeplearning.py -- allows module import without DL deps
- Lazy-imported validate_no_leakage in profiler.py -- avoids import-time dependency chain

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made torch imports lazy in prepare/deeplearning.py**
- **Found during:** Task 1 (import verification)
- **Issue:** Module-level `import torch` prevented importing prepare.deeplearning without torch installed
- **Fix:** Moved torch imports to TYPE_CHECKING block and inside functions that use them
- **Files modified:** python/src/gsd_ml/prepare/deeplearning.py
- **Verification:** All 17 modules import cleanly without torch installed
- **Committed in:** 5c0fa3d (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Essential fix for non-DL environments. No scope creep.

## Issues Encountered
- Python system packages restriction required creating a venv (.venv/) -- resolved by creating venv before pip install

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- gsd_ml package is pip-installable and fully tested
- Ready for npm package skeleton (plan 02) and subsequent phases
- DL/FT prepare modules require optional torch/transformers deps at runtime

## Self-Check: PASSED

All 21 key files verified present. Both task commits (5c0fa3d, 11c6bb1) verified in git log.

---
*Phase: 01-foundation*
*Completed: 2026-03-22*
