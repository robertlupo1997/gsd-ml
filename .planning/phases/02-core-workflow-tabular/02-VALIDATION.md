---
phase: 2
slug: core-workflow-tabular
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | `python/pyproject.toml` (pytest section) |
| **Quick run command** | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` |
| **Full suite command** | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m pytest python/tests/ -x -q`
- **After every plan wave:** Run `python -m pytest python/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 02-01-01 | 01 | 1 | PROF-01..04 | unit | `python -m pytest python/tests/test_profiler.py -x -q` | Yes | ⬜ pending |
| 02-01-02 | 01 | 1 | SCAF-03 | smoke | syntax check of train-tabular.py | Wave 0 | ⬜ pending |
| 02-02-01 | 02 | 1 | SCAF-01..04 | integration | workflow scaffolding test | N/A (workflow) | ⬜ pending |
| 02-02-02 | 02 | 1 | LOOP-01..06 | integration | workflow loop test | N/A (workflow) | ⬜ pending |
| 02-02-03 | 02 | 1 | GUARD-01..04 | unit | `python -m pytest python/tests/test_guardrails.py -x -q` | Yes | ⬜ pending |
| 02-02-04 | 02 | 1 | STATE-01,03,04 | unit | `python -m pytest python/tests/test_checkpoint.py test_results.py test_journal.py -x -q` | Yes | ⬜ pending |
| 02-02-05 | 02 | 1 | FIN-01..03 | unit | `python -m pytest python/tests/test_export.py test_retrospective.py -x -q` | Yes | ⬜ pending |
| 02-03-01 | 03 | 1 | TAB-01..04 | unit | `python -m pytest python/tests/test_baselines.py -x -q` | Yes | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `gsd-ml/templates/train-tabular.py` — static template needs creation and syntax validation
- [ ] End-to-end smoke test with a small CSV (iris-style) — manual verification

*Existing test infrastructure (162 tests) covers all Python utility requirements.*

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| .ml/ directory scaffolded | SCAF-01, SCAF-02 | Workflow orchestration, not a Python function | Run `/gsd:ml` on test CSV, verify .ml/ created with config.json, prepare.py, train.py |
| Git branch created | SCAF-04 | Git integration in workflow | Verify `ml/run-*` branch exists after workflow run |
| Edit/run/parse/keep/revert loop | LOOP-01..06 | Claude Code behavior, not unit-testable | Run workflow, verify commits on improvement, reverts on non-improvement |
| Git tag on best commit | FIN-03 | Git integration in workflow | Verify `ml/best-*` tag exists after workflow finalization |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
