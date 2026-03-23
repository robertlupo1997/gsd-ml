---
phase: 5
slug: supporting-skills
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-03-22
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | python/pyproject.toml |
| **Quick run command** | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` |
| **Full suite command** | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q`
- **After every plan wave:** Run `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | SKILL-01 | manual | Invoke `/gsd:ml-status` in project with `.ml/` | N/A | ⬜ pending |
| 05-01-02 | 01 | 1 | SKILL-03 | manual | Invoke `/gsd:ml-clean` in project with `.ml/` | N/A | ⬜ pending |
| 05-01-03 | 01 | 1 | SKILL-04 | manual | Invoke `/gsd:ml-diagnose` in project with `.ml/` | N/A | ⬜ pending |
| 05-02-01 | 02 | 1 | STATE-02, SKILL-02 | manual | Invoke `/gsd:ml-resume` in project with `.ml/checkpoint.json` | N/A | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. The underlying Python modules (checkpoint.py, results.py, diagnostics.py, state.py) are already fully tested from Phase 1 (162 tests passing). New code is skill files (YAML + markdown) and workflow files (markdown) executed by Claude Code as the runtime.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Status shows past runs | SKILL-01 | Skill file invoked by Claude Code runtime | Run experiment, then invoke `/gsd:ml-status` — verify table output with metrics |
| Resume loads checkpoint | STATE-02, SKILL-02 | Skill re-enters ml-run.md workflow | Start experiment, interrupt, invoke `/gsd:ml-resume` — verify loop continues |
| Clean removes .ml/ | SKILL-03 | Destructive operation on filesystem + git | Create `.ml/`, invoke `/gsd:ml-clean` — verify directory removed, branches optionally deleted |
| Diagnose runs standalone | SKILL-04 | Requires trained model from prior experiment | Run experiment, then invoke `/gsd:ml-diagnose` — verify diagnostic output printed |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: existing Python test suite runs after every commit
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
