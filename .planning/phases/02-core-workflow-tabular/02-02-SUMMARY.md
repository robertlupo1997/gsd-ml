---
phase: 02-core-workflow-tabular
plan: 02
subsystem: workflow
tags: [ml-workflow, experiment-loop, tabular, orchestration, git-branching]

requires:
  - phase: 01-foundation
    provides: "All 17 Python utilities (profiler, guardrails, checkpoint, results, journal, export, retrospective, baselines, prepare)"
provides:
  - "ml-run.md workflow for complete tabular experiment orchestration"
  - "4-phase workflow: profile, scaffold, loop, finalize"
  - "Python utility invocation patterns via python -c"
affects: [03-intelligence-tabular, 04-multi-domain, 06-polish]

tech-stack:
  added: []
  patterns: [workflow-driven-orchestration, python-c-bridge, selective-git-revert, json-stdout-contract, config-based-guardrails]

key-files:
  created:
    - gsd-ml/workflows/ml-run.md
  modified: []

key-decisions:
  - "Guardrails read start_time from config.json rather than in-memory timers to survive context resets"
  - "Selective revert: only train.py reverted on non-improvement, state files always preserved"
  - "Workflow structured as 4 sequential phases with numbered steps for Claude Code to follow"

patterns-established:
  - "Python utility bridge: all gsd_ml modules invoked via python -c in Bash"
  - "JSON stdout contract: train.py outputs last line as JSON with metric_value and metric_name"
  - "Selective revert pattern: git checkout -- train.py only, never state files"
  - "Config persistence: start_time stored in config.json for guardrail time checks"

requirements-completed: [PROF-01, PROF-03, PROF-04, SCAF-01, SCAF-02, SCAF-04, LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, GUARD-01, GUARD-02, GUARD-03, GUARD-04, STATE-01, STATE-03, STATE-04, TAB-04, FIN-01, FIN-02, FIN-03]

duration: 2min
completed: 2026-03-22
---

# Phase 2 Plan 02: ML Run Workflow Summary

**Complete tabular experiment orchestration workflow with profile/scaffold/loop/finalize phases, calling all gsd_ml Python utilities via python -c bridge pattern**

## Performance

- **Duration:** 2 min
- **Started:** 2026-03-22T23:49:09Z
- **Completed:** 2026-03-22T23:51:30Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- Created 493-line ml-run.md workflow covering the complete experiment lifecycle
- All 8 required Python modules referenced with correct import patterns and function signatures
- Addressed all 5 pitfalls from research (selective revert, JSON parsing, working directory, git branch timing, guardrail persistence)
- 23 requirements covered by workflow instructions

## Task Commits

Each task was committed atomically:

1. **Task 1: Create ml-run.md workflow** - `0f47b3e` (feat)

## Files Created/Modified
- `gsd-ml/workflows/ml-run.md` - Complete 4-phase experiment orchestration workflow (493 lines)

## Decisions Made
- Guardrail time checks read start_time from config.json (not in-memory timers) to survive context resets per research pitfall 5
- Selective revert pattern: only train.py reverted, state files always preserved per research pitfall 1
- Workflow structured as numbered steps within 4 labeled phases for sequential Claude Code execution

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- ml-run.md workflow complete, ready for train-tabular.py template creation (plan 02-01 or 02-03)
- All Python utilities already tested (162 tests passing)
- Workflow references template at `~/.claude/gsd-ml/templates/train-tabular.py` which needs creation

---
*Phase: 02-core-workflow-tabular*
*Completed: 2026-03-22*
