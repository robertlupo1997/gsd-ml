# Documentation Fixes Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix all documentation inaccuracies and gaps identified by the codebase audit — CLAUDE.md, README.md, ml.md skill, pyproject.toml, and Python package init files.

**Architecture:** Direct file edits across 7 files. No new features, no code changes — purely documentation alignment with shipped v1.0 codebase.

**Tech Stack:** Markdown, YAML, TOML, Python

---

### Task 1: Fix ml.md skill file

**Files:**
- Modify: `commands/gsd-ml/ml.md`

**Step 1: Update the skill file**

Replace the entire file with:

```yaml
---
name: gsd:ml
description: Run an autonomous ML experiment
argument-hint: "<dataset> <target> [--domain tabular|dl|ft] [--task <task_type>] [--model-name <model>]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---
<objective>Run an autonomous ML experiment: profile dataset, scaffold .ml/ directory, iterate on train.py, export best model. Supports tabular (sklearn/XGBoost/LightGBM), deep learning (timm/transformers), and fine-tuning (LoRA/QLoRA) domains.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-run.md</execution_context>
<context>Dataset path: first argument. Target column: second argument (optional for image classification). Domain defaults to tabular. Use --domain dl for deep learning, --domain ft for fine-tuning. Use --task for DL subtask (image_classification, text_classification). Use --model-name for FT base model.

Arguments: $ARGUMENTS</context>
<process>Follow the ml-run workflow step by step. Do not skip phases. Do not modify prepare.py.</process>
<references>@~/.claude/gsd-ml/references/metric-map.md</references>
```

**Step 2: Verify YAML parses correctly**

Run: `head -6 commands/gsd-ml/ml.md`
Expected: Valid YAML frontmatter with `---` delimiters and all 4 fields.

**Step 3: Commit**

```bash
git add commands/gsd-ml/ml.md
git commit -m "docs: fix ml.md skill — add all domain flags and multi-domain objective"
```

---

### Task 2: Update README.md

**Files:**
- Modify: `README.md`

**Step 1: Update Quick Start section**

Replace lines 32-40 (Quick Start section) with:

```markdown
## Quick Start

In Claude Code, run:

```
/gsd:ml data.csv target_column
```

This profiles your dataset, scaffolds a `.ml/` experiment directory, runs iterative training with automatic keep/revert decisions, and exports the best model.

For other domains:

```
/gsd:ml images/ --domain dl --task image_classification
/gsd:ml data.csv target --domain dl --task text_classification
/gsd:ml data.jsonl --domain ft --model-name meta-llama/Llama-3-8B
```
```

**Step 2: Update How It Works section**

Replace lines 61-76 (How It Works section) with:

```markdown
## How It Works

```
Skill (/gsd:ml) -> Workflow (ml-run.md) -> Claude Code executes with native tools
```

1. **Skills** (`~/.claude/commands/gsd-ml/`) are Claude Code slash commands with YAML frontmatter
2. **Workflows** (`~/.claude/gsd-ml/workflows/`) are step-by-step markdown instructions that Claude Code follows
3. **Templates** (`~/.claude/gsd-ml/templates/`) provide starter train.py files for each domain (tabular, DL image, DL text, fine-tuning)
4. **References** (`~/.claude/gsd-ml/references/`) are lookup tables (e.g., metric-map.md maps metrics to sklearn scoring strings)
5. Claude Code reads/writes files, runs training via Bash, parses metrics, and manages experiment state through git

Experiment state lives in `.ml/`:
- `config.json` -- experiment configuration (domain, target, metric, guardrails)
- `checkpoint.json` -- current progress (iteration, best score, keeps/reverts)
- `results.jsonl` -- metric history across iterations
- `experiments.md` -- human-readable journal of each iteration
```

Note: also fix `results.csv` → `results.jsonl` and `journal.jsonl` → `experiments.md` to match actual file names used in ml-run.md.

**Step 3: Add GPU note to Domains table**

After the Domains table (line 49), add:

```markdown

> DL and FT domains check for GPU availability at startup. CPU-only machines get a warning but can still run experiments (slowly).
```

**Step 4: Verify README renders correctly**

Run: `wc -l README.md`
Expected: ~105 lines (up from 92).

**Step 5: Commit**

```bash
git add README.md
git commit -m "docs: update README — multi-domain quick start, templates/references, fix state file names"
```

---

### Task 3: Rewrite CLAUDE.md for v1.0

**Files:**
- Modify: `CLAUDE.md`

**Step 1: Replace CLAUDE.md entirely**

The file should describe the shipped v1.0 codebase for maintainers, not the pre-v1.0 porting plan. Replace with:

```markdown
# gsd-ml

Claude Code native autonomous ML research tool. Published as `gsd-ml@0.1.0` on npm.

## Architecture

**Distribution:** npm package installs skills, workflows, templates, and references into `~/.claude/`. Python ML utilities ship as a separate pip package (`gsd_ml`).

**Key pattern:** Skills → Workflows → Claude Code executes with native tools (Read/Write/Edit/Bash/git)

**Installed structure:**
```
~/.claude/commands/gsd-ml/     # 5 skill files (slash commands)
  ml.md, ml-status.md, ml-resume.md, ml-clean.md, ml-diagnose.md

~/.claude/gsd-ml/              # workflows, templates, references
  workflows/   ml-run.md, ml-status.md, ml-resume.md, ml-clean.md, ml-diagnose.md
  templates/   train-tabular.py, train-dl-image.py, train-dl-text.py, train-ft.py
  references/  metric-map.md
```

**Python package:** `python/src/gsd_ml/` — 17 modules, 188 tests
- Core: profiler, state, checkpoint, guardrails, results, journal, export, retrospective
- Intelligence: diagnostics, drafts, stagnation
- Baselines: tabular, deeplearning, finetuning
- Prepare: tabular, deeplearning, finetuning

## Key Decisions

| Decision | Rationale |
|----------|-----------|
| Claude Code does everything | No subprocess spawning = no double billing, full context |
| npm + pip distribution | npm for skills/workflows (GSD pattern), pip for Python ML utilities |
| Static templates with `__PLACEHOLDER__` | Replaced Jinja2; scaffold phase does string replacement |
| DL split into image + text templates | Simpler than one template with conditionals |
| `python3 -c` bridge calls | All workflows invoke gsd_ml via `python3 -c "from gsd_ml.X import Y; ..."` |
| Guardrails read start_time from config.json | Survives context resets unlike in-memory timers |
| No Optuna | Claude Code iterates manually; HPO framework unnecessary |

## Predecessor

Redesigned from [mlforge](https://github.com/robertlupo1997/mlforge). Same Python utilities, but Claude Code IS the researcher instead of being spawned as a subprocess. Dropped: engine.py, cli.py, swarm/, hooks.py, progress.py, plugins.py, Jinja2 templates.

## Planning

Project planning artifacts are in `.planning/`. v1.0 milestone archived to `.planning/milestones/`.
```

**Step 2: Verify file is clean**

Run: `wc -l CLAUDE.md && head -3 CLAUDE.md`
Expected: ~45 lines, starts with `# gsd-ml`.

**Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "docs: rewrite CLAUDE.md for shipped v1.0 — replace porting plan with architecture reference"
```

---

### Task 4: Update pyproject.toml metadata

**Files:**
- Modify: `python/pyproject.toml`

**Step 1: Add missing metadata fields**

Replace the `[project]` section (lines 5-17) with:

```toml
[project]
name = "gsd-ml"
version = "0.1.0"
description = "Python ML utilities for gsd-ml — profiling, checkpointing, diagnostics, baselines, and state management"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Robert Lupo"}]
readme = "README.md"
keywords = ["machine-learning", "claude-code", "autonomous-research", "ml-experiments"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
]
dependencies = [
    "scikit-learn>=1.5",
    "pandas>=2.0",
    "numpy>=2.0",
    "xgboost>=2.0",
    "lightgbm>=4.0",
    "pyarrow>=15.0",
]

[project.urls]
Homepage = "https://github.com/robertlupo1997/gsd-ml"
Repository = "https://github.com/robertlupo1997/gsd-ml"
Issues = "https://github.com/robertlupo1997/gsd-ml/issues"
```

**Step 2: Verify TOML parses**

Run: `cd python && python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['name'])" && cd ..`
Expected: `gsd-ml`

**Step 3: Commit**

```bash
git add python/pyproject.toml
git commit -m "docs: add author, license, classifiers, URLs to pyproject.toml"
```

---

### Task 5: Add Python subpackage docstrings

**Files:**
- Modify: `python/src/gsd_ml/baselines/__init__.py`
- Modify: `python/src/gsd_ml/prepare/__init__.py`

**Step 1: Add docstrings**

`baselines/__init__.py`:
```python
"""Baseline computation for ML experiments — naive strategies to establish minimum performance bars."""
```

`prepare/__init__.py`:
```python
"""Data preparation modules — frozen pipelines copied into experiment directories."""
```

**Step 2: Verify imports still work**

Run: `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python3 -c "from gsd_ml.baselines.tabular import compute_baselines; print('OK')" && python3 -c "from gsd_ml.prepare.tabular import load_data; print('OK')"`
Expected: `OK` twice.

**Step 3: Commit**

```bash
git add python/src/gsd_ml/baselines/__init__.py python/src/gsd_ml/prepare/__init__.py
git commit -m "docs: add docstrings to baselines and prepare subpackage inits"
```

---

### Task 6: Run full test suite and push

**Step 1: Run Python tests**

Run: `cd /home/tlupo/gsd-ml && source .venv/bin/activate && python -m pytest python/tests/ -q`
Expected: `188 passed`

**Step 2: Run npm pack dry-run**

Run: `npm pack --dry-run 2>&1 | tail -5`
Expected: 18 files, gsd-ml@0.1.0

**Step 3: Final commit and push**

```bash
git push origin main
```
