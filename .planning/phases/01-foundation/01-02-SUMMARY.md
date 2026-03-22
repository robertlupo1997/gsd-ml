---
phase: 01-foundation
plan: 02
subsystem: infra
tags: [npm, installer, claude-code, skill]

# Dependency graph
requires: []
provides:
  - npm package skeleton with install.js
  - /gsd:ml stub skill file
  - ml-run stub workflow
affects: [02-ml-workflow, 03-intelligence]

# Tech tracking
tech-stack:
  added: [node.js installer]
  patterns: [GSD install pattern with copyWithPathReplacement]

key-files:
  created:
    - package.json
    - bin/install.js
    - commands/gsd-ml/ml.md
    - gsd-ml/workflows/ml-run.md
  modified: []

key-decisions:
  - "Followed GSD install.js pattern exactly: copyWithPathReplacement for .md files"
  - "Python validation as warning not error: ML workflows need gsd_ml but installer should not fail"

patterns-established:
  - "Install pattern: commands/gsd-ml/ to ~/.claude/commands/gsd-ml/, gsd-ml/ to ~/.claude/gsd-ml/"
  - "Path replacement: ~/.claude/ references replaced with actual install path in .md files"

requirements-completed: [PKG-01, PKG-02, PKG-04]

# Metrics
duration: 1min
completed: 2026-03-22
---

# Phase 1 Plan 2: npm Package Skeleton Summary

**npm package with install.js that copies /gsd:ml skill and ml-run workflow to ~/.claude/, with Python gsd_ml validation**

## Performance

- **Duration:** 1 min
- **Started:** 2026-03-22T18:55:50Z
- **Completed:** 2026-03-22T18:56:57Z
- **Tasks:** 1
- **Files modified:** 4

## Accomplishments
- npm package.json with bin entry pointing to bin/install.js
- install.js copies commands and workflows to ~/.claude/ following GSD pattern
- Stub /gsd:ml skill file installed and working
- Python package validation with helpful install instructions on missing

## Task Commits

Each task was committed atomically:

1. **Task 1: Create package.json, install.js, and stub skill** - `6f3bafb` (feat)

## Files Created/Modified
- `package.json` - npm package configuration with bin entry
- `bin/install.js` - Installer that copies skills/workflows to ~/.claude/ with path replacement
- `commands/gsd-ml/ml.md` - Stub /gsd:ml skill file with YAML frontmatter
- `gsd-ml/workflows/ml-run.md` - Stub ml-run workflow placeholder

## Decisions Made
- Followed GSD install.js pattern: copyWithPathReplacement for .md files, clean install (rm + recreate)
- Python validation as warning not error -- installer succeeds even without gsd_ml pip package
- Single-runtime installer (Claude Code only) -- no multi-runtime support needed unlike GSD

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- npm package skeleton ready for content: workflows, references, templates in Phase 2
- Python package skeleton (plan 01) provides gsd_ml module structure
- /gsd:ml skill stub wired to ml-run.md workflow (to be filled in Phase 2)

---
*Phase: 01-foundation*
*Completed: 2026-03-22*
