---
phase: 06
slug: polish-release
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-23
---

# Phase 06 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.x |
| **Config file** | python/pyproject.toml |
| **Quick run command** | `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python -m pytest python/tests/ -x -q` |
| **Full suite command** | `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python -m pytest python/tests/ -v` |
| **Estimated runtime** | ~3 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick command
- **After every plan wave:** Run full suite
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 5 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | Quality | integration | `npm pack --dry-run` | N/A | pending |
| 06-01-02 | 01 | 1 | Quality | manual | verify workflow error messages | N/A | pending |
| 06-02-01 | 02 | 1 | Quality | manual | review README content | N/A | pending |
| 06-02-02 | 02 | 1 | Quality | integration | `npm publish --dry-run` | N/A | pending |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. 188 tests already exist.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| README accuracy | Docs | Content review needed | Read README, verify install steps work |
| Error messages helpful | Error handling | Subjective quality | Trigger each error path, verify actionable messages |
| npm install works | Publish | Requires actual install | `npm pack && npm install gsd-ml-0.1.0.tgz` |

---

## Validation Sign-Off

- [ ] All tasks have automated verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 5s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
