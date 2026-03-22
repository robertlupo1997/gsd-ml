# Roadmap: gsd-ml

## Overview

Build gsd-ml as a Claude Code native ML research tool following GSD patterns. Start with npm package skeleton and Python utilities (Phase 1), prove the core experiment loop works for tabular ML (Phase 2), add the intelligence layer (Phase 3), extend to DL and fine-tuning (Phase 4), add supporting skills (Phase 5), and polish for release (Phase 6).

## Phases

- [x] **Phase 1: Foundation** - npm package skeleton + Python utilities ported from mlforge (2026-03-22)
- [ ] **Phase 2: Core Workflow** - End-to-end tabular experiment loop via Claude Code
- [ ] **Phase 3: Intelligence Layer** - Diagnostics, stagnation, multi-draft
- [ ] **Phase 4: DL + Fine-Tuning** - Deep learning and fine-tuning domains
- [ ] **Phase 5: Supporting Skills** - Resume, status, clean, diagnose
- [ ] **Phase 6: Polish + Release** - Tests, docs, error handling, npm publish

## Phase Details

### Phase 1: Foundation
**Goal**: npm package installs into ~/.claude/, Python gsd_ml package importable with all ported utilities
**Depends on**: Nothing (first phase)
**Requirements**: PKG-01, PKG-02, PKG-03, PKG-04
**Success Criteria** (what must be TRUE):
  1. `npm install -g gsd-ml` copies skills/workflows/references/templates to ~/.claude/
  2. `/gsd:ml` appears as available skill in Claude Code
  3. `python -c "from gsd_ml.profiler import profile_dataset"` works
  4. `python -c "from gsd_ml.guardrails import check_guardrails"` works
  5. All ported Python utilities pass tests
**Plans:** 2/2 complete

Plans:
- [x] 01-01-PLAN.md — Port all 17 Python modules + tests (162 passing)
- [x] 01-02-PLAN.md — npm package skeleton (install.js, stub skill)

### Phase 2: Core Workflow (Tabular)
**Goal**: `/gsd:ml dataset.csv target` runs a complete tabular ML experiment end-to-end
**Depends on**: Phase 1
**Requirements**: PROF-01, PROF-02, PROF-03, PROF-04, SCAF-01, SCAF-02, SCAF-03, SCAF-04, LOOP-01, LOOP-02, LOOP-03, LOOP-04, LOOP-05, LOOP-06, GUARD-01, GUARD-02, GUARD-03, GUARD-04, STATE-01, STATE-03, STATE-04, TAB-01, TAB-02, TAB-03, TAB-04, FIN-01, FIN-02, FIN-03
**Success Criteria** (what must be TRUE):
  1. Claude Code profiles a CSV and auto-detects classification vs regression
  2. `.ml/` directory scaffolded with prepare.py, train.py, config.json
  3. Claude Code iterates: edit train.py -> run -> parse metric -> keep/revert
  4. Git branch created, commits on keep, reverts on non-improvement
  5. Guardrails stop the loop when budget exhausted
  6. Best model exported to .ml/artifacts/ with metadata
  7. Retrospective markdown generated
**Plans:** 2 plans

Plans:
- [ ] 02-01-PLAN.md — Static template (train-tabular.py), metric reference, skill file update
- [ ] 02-02-PLAN.md — Complete ml-run.md workflow (profile, scaffold, loop, finalize)

### Phase 3: Intelligence Layer
**Goal**: Smart iteration with diagnostics, stagnation branching, and multi-draft exploration
**Depends on**: Phase 2
**Requirements**: INTEL-01, INTEL-02, INTEL-03, INTEL-04, INTEL-05, INTEL-06, INTEL-07
**Success Criteria** (what must be TRUE):
  1. Baselines computed before experimentation; model must beat them to be kept
  2. Diagnostics run after each experiment; results injected into next iteration
  3. Stagnation detected after N reverts; triggers branch to new model family
  4. Multi-draft phase (when enabled) explores diverse initial solutions
**Plans**: TBD

### Phase 4: DL + Fine-Tuning
**Goal**: Deep learning and fine-tuning domains work end-to-end
**Depends on**: Phase 3
**Requirements**: DL-01, DL-02, DL-03, DL-04, FT-01, FT-02, FT-03, FT-04
**Success Criteria** (what must be TRUE):
  1. `/gsd:ml images/ target --domain dl` runs image classification experiments
  2. `/gsd:ml data.jsonl target --domain ft --model-name meta-llama/Llama-3-8B` runs fine-tuning
  3. Domain-specific baselines computed for DL and FT
  4. GPU auto-detected and surfaced for DL/FT domains
**Plans**: TBD

### Phase 5: Supporting Skills
**Goal**: Full skill suite (resume, status, clean, diagnose) works
**Depends on**: Phase 2
**Requirements**: STATE-02, SKILL-01, SKILL-02, SKILL-03, SKILL-04
**Success Criteria** (what must be TRUE):
  1. `/gsd:ml-status` shows past runs with metrics, cost, keeps/reverts
  2. `/gsd:ml-resume` loads checkpoint and continues experiment loop
  3. `/gsd:ml-clean` removes .ml/ directories and orphaned git branches
  4. `/gsd:ml-diagnose` runs diagnostics on current model without entering loop
**Plans**: TBD

### Phase 6: Polish + Release
**Goal**: Production-ready npm package published
**Depends on**: Phase 4, Phase 5
**Requirements**: (quality requirements, not feature requirements)
**Success Criteria** (what must be TRUE):
  1. Python test suite passes for all gsd_ml utilities
  2. README.md documents installation and usage
  3. Error handling covers missing deps, corrupt state, git issues
  4. `npm publish` succeeds and package installable from registry
**Plans**: TBD

## Progress

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/2 | Complete | 2026-03-22 |
| 2. Core Workflow | 0/2 | Planned | - |
| 3. Intelligence | 0/TBD | Not started | - |
| 4. DL + FT | 0/TBD | Not started | - |
| 5. Supporting Skills | 0/TBD | Not started | - |
| 6. Polish | 0/TBD | Not started | - |
