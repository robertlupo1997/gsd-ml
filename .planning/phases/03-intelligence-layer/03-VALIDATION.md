---
phase: 3
slug: intelligence-layer
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.0.2 |
| **Config file** | `python/pyproject.toml` |
| **Quick run command** | `source .venv/bin/activate && python -m pytest python/tests/ -x -q` |
| **Full suite command** | `source .venv/bin/activate && python -m pytest python/tests/ -q` |
| **Estimated runtime** | ~5 seconds |

---

## Sampling Rate

- **After every task commit:** Run `source .venv/bin/activate && python -m pytest python/tests/ -x -q`
- **After every plan wave:** Run `source .venv/bin/activate && python -m pytest python/tests/ -q`
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | INTEL-01 | unit | `python -m pytest python/tests/test_baselines.py -x` | Yes | ⬜ pending |
| 03-01-02 | 01 | 1 | INTEL-02 | unit | `python -m pytest python/tests/test_baselines.py::TestPassesBaselineGate -x` | Yes | ⬜ pending |
| 03-01-03 | 01 | 1 | INTEL-03 | unit | `python -m pytest python/tests/test_diagnostics.py -x` | Yes | ⬜ pending |
| 03-01-04 | 01 | 1 | INTEL-04 | manual-only | Verify diagnostics.json read in workflow | N/A | ⬜ pending |
| 03-01-05 | 01 | 1 | INTEL-05 | unit | `python -m pytest python/tests/test_drafts.py -x` | Yes | ⬜ pending |
| 03-01-06 | 01 | 1 | INTEL-06 | unit | `python -m pytest python/tests/test_stagnation.py -x` | Yes | ⬜ pending |
| 03-01-07 | 01 | 1 | INTEL-07 | unit | `python -m pytest python/tests/test_stagnation.py -x` | Yes | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. All 54 intelligence tests pass. Phase work is workflow integration (markdown), not new Python code.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Diagnostics injected into next iteration prompt | INTEL-04 | Workflow behavior — Claude reads diagnostics.json before editing train.py | Verify ml-run.md includes instruction to read .ml/diagnostics.json before Step 3.2 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 10s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
