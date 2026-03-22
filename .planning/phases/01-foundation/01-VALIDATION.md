---
phase: 1
slug: foundation
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 7.x (Python), manual verification (npm) |
| **Config file** | python/pyproject.toml (pytest config section) |
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

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01 | 1 | PKG-03 | unit | `python -c "import gsd_ml"` | W0 | pending |
| 1-01-02 | 01 | 1 | PKG-03 | unit | `python -m pytest tests/test_profiler.py -x` | W0 | pending |
| 1-01-03 | 01 | 1 | PKG-03 | unit | `python -m pytest tests/test_state.py -x` | W0 | pending |
| 1-01-04 | 01 | 1 | PKG-03 | unit | `python -m pytest tests/test_guardrails.py -x` | W0 | pending |
| 1-02-01 | 02 | 1 | PKG-01 | manual | `ls ~/.claude/commands/gsd-ml/ml.md` | W0 | pending |
| 1-02-02 | 02 | 1 | PKG-02 | manual | `ls ~/.claude/gsd-ml/workflows/` | W0 | pending |
| 1-02-03 | 02 | 1 | PKG-04 | integration | `node bin/install.js && python -c "from gsd_ml.profiler import profile_dataset"` | W0 | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [ ] `python/tests/test_profiler.py` — test profile_dataset import and basic function
- [ ] `python/tests/test_state.py` — test SessionState dataclass
- [ ] `python/tests/test_guardrails.py` — test check_guardrails with JSON config
- [ ] `python/tests/conftest.py` — shared fixtures (tmp dirs, sample data)
- [ ] pytest installed in dev dependencies

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| npm install copies skills to ~/.claude/ | PKG-01 | Requires global npm install | Run `npm install -g .` then verify `ls ~/.claude/commands/gsd-ml/` |
| /gsd:ml appears in Claude Code | PKG-01 | Requires Claude Code runtime | Start Claude Code, check skill list |
| install.js validates Python package | PKG-04 | Requires end-to-end install | Run installer, check validation output |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
