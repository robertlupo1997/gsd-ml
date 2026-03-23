---
phase: 06-polish-release
plan: 01
subsystem: workflows
tags: [python3, error-handling, npm, bridge-validation, pre-flight]

# Dependency graph
requires:
  - phase: 05-supporting-skills
    provides: All 5 workflow files and skill files
provides:
  - Hardened workflow error handling with pre-flight checks
  - Standardized python3 calls across all workflows
  - Validated Python bridge call signatures
  - Publish-ready package.json with homepage and bugs fields
affects: [06-polish-release]

# Tech tracking
tech-stack:
  added: []
  patterns: [pre-flight dependency check, ResourceGuardrails API pattern]

key-files:
  created: []
  modified:
    - gsd-ml/workflows/ml-run.md
    - gsd-ml/workflows/ml-resume.md
    - gsd-ml/workflows/ml-status.md
    - gsd-ml/workflows/ml-clean.md
    - gsd-ml/workflows/ml-diagnose.md
    - package.json

key-decisions:
  - "Fixed ml-resume.md: replaced non-existent check_guardrails() with ResourceGuardrails(config, dir).should_stop(state)"
  - "Pre-flight checks kept minimal per user constraint: gsd_ml import check, git repo check, .ml/ directory check as applicable"

patterns-established:
  - "Pre-flight check pattern: python3 -c import gsd_ml at workflow start, actionable error on failure"
  - "python3 standardization: all workflows use python3 -c consistently (never bare python)"

requirements-completed: [POLISH-01, POLISH-03]

# Metrics
duration: 3min
completed: 2026-03-23
---

# Phase 6 Plan 01: Error Handling + Bridge Validation Summary

**Standardized all 5 workflows to python3, added pre-flight dependency checks, fixed ResourceGuardrails bridge mismatch in ml-resume.md, and polished package.json for npm publish**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-23T02:14:01Z
- **Completed:** 2026-03-23T02:17:29Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- Replaced all 30+ `python -c` calls with `python3 -c` across ml-run.md (the only file with bare python)
- Added Pre-flight Checks section to all 5 workflow files with actionable error messages
- Fixed bridge call mismatch: ml-resume.md called non-existent `check_guardrails()` function, replaced with correct `ResourceGuardrails` API
- Added homepage and bugs fields to package.json; verified version 0.1.0, files array, bin field
- Full Python test suite green (188 passed), npm pack succeeds (18 files, 98.6 kB)

## Task Commits

Each task was committed atomically:

1. **Task 1: Validate Python bridge calls and standardize python3** - `7047d7f` (feat)
2. **Task 2: Polish package.json and run test suite** - `35df0af` (chore)

## Files Created/Modified
- `gsd-ml/workflows/ml-run.md` - Standardized 30+ python calls to python3, added pre-flight checks
- `gsd-ml/workflows/ml-resume.md` - Added pre-flight checks, fixed check_guardrails bridge call
- `gsd-ml/workflows/ml-status.md` - Added pre-flight gsd_ml import check
- `gsd-ml/workflows/ml-clean.md` - Added pre-flight .ml/ directory existence check
- `gsd-ml/workflows/ml-diagnose.md` - Added pre-flight gsd_ml import + .ml/ + checkpoint checks
- `package.json` - Added homepage and bugs fields for npm publish readiness

## Decisions Made
- Fixed ml-resume.md bridge mismatch: `check_guardrails(config)` does not exist in gsd_ml.guardrails module. Replaced with `ResourceGuardrails(config, Path('.ml')).should_stop(state)` which is the actual API. This was the only bridge call mismatch found across all 37+ calls.
- Pre-flight checks kept minimal and actionable per user decision -- only check where failure is likely and confusing (missing deps, missing state dirs). No try/catch on every bridge call.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed non-existent check_guardrails function in ml-resume.md**
- **Found during:** Task 1 (bridge call audit)
- **Issue:** ml-resume.md Step 4 called `from gsd_ml.guardrails import check_guardrails` which does not exist. The actual API is `ResourceGuardrails` class with `should_stop(state)` method.
- **Fix:** Replaced with correct `ResourceGuardrails(config, Path('.ml'))` instantiation and `should_stop(state)` / `stop_reason(state)` calls.
- **Files modified:** gsd-ml/workflows/ml-resume.md
- **Verification:** Confirmed via `python3 -c "from gsd_ml.guardrails import ResourceGuardrails"` succeeds
- **Committed in:** 7047d7f (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Bridge mismatch fix was essential for correctness. No scope creep.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All workflows hardened with pre-flight checks and correct bridge calls
- package.json publish-ready with all metadata fields
- Ready for Plan 02: README.md documentation and npm publish verification

---
*Phase: 06-polish-release*
*Completed: 2026-03-23*
