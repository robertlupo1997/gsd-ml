---
phase: 1
slug: foundation
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-03-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x |
| **Config file** | python/pyproject.toml |
| **Quick run command** | `cd python && python -m pytest tests/ -x -q` |
| **Full suite command** | `cd python && python -m pytest tests/ -v` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd python && python -m pytest tests/ -x -q`
- **After every plan wave:** Run `cd python && python -m pytest tests/ -v`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | Status |
|---------|------|------|-------------|-----------|-------------------|--------|
| 1-01-01 | 01 | 1 | PKG-03 | integration | `python -c "from gsd_ml import ..."` (all 17 modules) | pending |
| 1-01-02 | 01 | 1 | PKG-03 | unit | `python -m pytest tests/ -v` | pending |
| 1-02-01 | 02 | 1 | PKG-01, PKG-02, PKG-04 | integration | `node bin/install.js && ls ~/.claude/commands/gsd-ml/ml.md` | pending |

---

## Wave 0 Requirements

- [ ] pytest installed via dev dependencies in pyproject.toml

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| /gsd:ml appears in Claude Code | PKG-01 | Requires Claude Code runtime | Start Claude Code, check skill list |

---

## Validation Sign-Off

- [ ] All tasks have automated verify
- [ ] Sampling continuity maintained
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
