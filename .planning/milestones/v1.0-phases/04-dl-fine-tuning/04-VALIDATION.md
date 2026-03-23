---
phase: 4
slug: dl-fine-tuning
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-03-22
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `python/pyproject.toml` |
| **Quick run command** | `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python -m pytest python/tests/ -x -q` |
| **Full suite command** | `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python -m pytest python/tests/ -v` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run quick run command
- **After every plan wave:** Run full suite command
- **Before `/gsd:verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | DL-01 | unit | `pytest python/tests/test_templates.py::test_dl_image_template -x` | No - W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | DL-02 | unit | `pytest python/tests/test_templates.py::test_dl_text_template -x` | No - W0 | ⬜ pending |
| 04-01-03 | 01 | 1 | DL-03 | unit | `pytest python/tests/test_prepare_dl.py::test_get_device_info -x` | No - W0 | ⬜ pending |
| 04-01-04 | 01 | 1 | DL-04 | unit | `pytest python/tests/test_baselines.py::TestDLBaselines -x` | No - W0 | ⬜ pending |
| 04-02-01 | 02 | 1 | FT-01 | unit | `pytest python/tests/test_templates.py::test_ft_template -x` | No - W0 | ⬜ pending |
| 04-02-02 | 02 | 1 | FT-02 | unit | `pytest python/tests/test_templates.py::test_ft_model_loading -x` | No - W0 | ⬜ pending |
| 04-02-03 | 02 | 1 | FT-03 | unit | `pytest python/tests/test_templates.py::test_ft_metrics -x` | No - W0 | ⬜ pending |
| 04-02-04 | 02 | 1 | FT-04 | unit | `pytest python/tests/test_baselines.py::TestFTBaselines -x` | No - W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `python/tests/test_templates.py` — template content verification tests (DL-01, DL-02, FT-01, FT-02, FT-03)
- [ ] `python/tests/test_baselines.py` — add TestDLBaselines and TestFTBaselines classes (DL-04, FT-04)
- [ ] `python/tests/test_prepare_dl.py` — GPU detection test (DL-03)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| DL workflow runs end-to-end with image data | DL-01 | Requires GPU + image dataset | Run `/gsd:ml images/ target --domain dl` with sample data |
| FT workflow runs end-to-end with JSONL data | FT-01 | Requires GPU + model download | Run `/gsd:ml data.jsonl target --domain ft --model-name ...` |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
