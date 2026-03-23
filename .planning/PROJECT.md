# gsd-ml

## What This Is

A Claude Code native autonomous ML research tool, distributed as an npm package following the GSD (get-shit-done-cc) pattern. Users invoke `/gsd:ml dataset.csv target_column` and Claude Code itself becomes the ML researcher -- profiling data, writing training scripts, running experiments, tracking results via git, and iterating until budget is exhausted. Supports tabular ML, deep learning, and LLM fine-tuning.

## Core Value

Claude Code autonomously runs structured ML experiments with full guardrails, git state tracking, and crash recovery -- without spawning subprocess agents or double-billing API costs.

## Requirements

### Validated

- ✓ Claude Code can profile a dataset and auto-detect task type, metric, and direction — Phase 2
- ✓ Claude Code scaffolds a `.ml/` experiment directory with frozen prepare.py and mutable train.py — Phase 2
- ✓ Claude Code runs the experiment loop: edit train.py, run it, parse metrics, keep/revert via git — Phase 2
- ✓ Guardrails enforce cost, time, experiment count, and disk space limits — Phase 2
- ✓ Tabular domain works (sklearn, XGBoost, LightGBM) — Phase 2
- ✓ Diagnostics analyze where the model fails and inject findings into next iteration — Phase 3
- ✓ Multi-draft phase explores 3-5 diverse initial solutions before linear iteration — Phase 3
- ✓ Stagnation detection branches to new model family after N consecutive reverts — Phase 3
- ✓ Deep learning domain works (PyTorch, timm, transformers) — Phase 4
- ✓ Fine-tuning domain works (peft, trl, LoRA, QLoRA) — Phase 4
- ✓ Checkpoint/resume survives context resets and session restarts — Phase 5
- ✓ `/gsd:ml-status` shows past experiment runs — Phase 5
- ✓ `/gsd:ml-resume` resumes an interrupted experiment — Phase 5
- ✓ `/gsd:ml-clean` removes old experiment artifacts — Phase 5
- ✓ npm package installs skills, workflows, references, templates into ~/.claude/ — Phase 1
- ✓ Python utilities installable via pip/uv for ML-specific operations — Phase 1

### Active

### Out of Scope

- Web UI or dashboard -- CLI/Claude Code only, terminal output and log files
- Cloud orchestration (AWS/GCP job submission) -- local-first, single machine
- Swarm/multi-agent mode -- dropped from mlforge; may revisit in v2
- Real-time data ingestion -- batch input (CSV, Parquet, JSON, JSONL)
- Building LLMs from scratch -- fine-tuning existing models only
- Replacing GSD -- gsd-ml is a domain-specific companion, not a fork

## Current State

**v1.0 shipped** 2026-03-23. Published as `gsd-ml@0.1.0` on npm.
- 2,057 LOC Python (17 modules), 2,082 LOC tests (188 passing), 2,927 LOC workflows/skills/templates
- 3 ML domains: tabular (sklearn/XGBoost/LightGBM), deep learning (timm/transformers), fine-tuning (LoRA/QLoRA)
- 5 skills: `/gsd:ml`, `/gsd:ml-status`, `/gsd:ml-resume`, `/gsd:ml-clean`, `/gsd:ml-diagnose`

## Context

**Predecessor:** mlforge (github.com/robertlupo1997/mlforge) proved autonomous ML experimentation works with 609 tests across 3 domains. But it spawns `claude -p` subprocesses -- double billing, JSON IPC overhead, no context continuity.

**GSD pattern:** GSD (get-shit-done-cc) is an npm package that installs skills, workflows, references, and templates into `~/.claude/`. gsd-ml follows this exact pattern for ML research.

**Key insight:** ~80% of mlforge's Python utilities (profiler, diagnostics, baselines, guardrails, state, checkpoint) are pure functions with no subprocess dependencies. They carry directly into gsd-ml as a Python package called via `python -c "..."` from Claude Code.

**What changes:** The experiment loop moves from Python (engine.py spawning `claude -p`) to a workflow .md file that Claude Code executes directly using its native tools (Read/Write/Edit/Bash/git).

## Constraints

- **Distribution**: npm package (like GSD) -- must install into `~/.claude/` following the same patterns
- **Python utilities**: Shipped as a separate pip-installable package (`gsd_ml`) -- ML ecosystem is Python-first
- **Claude Code**: Must work within Claude Code's tool model (Read, Write, Edit, Bash, git via Bash)
- **State persistence**: `.ml/` directory with checkpoint.json survives context resets
- **No subagents for loop**: The experiment loop is sequential; Claude Code runs it directly, not via spawned agents

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Claude Code does everything | No subprocess spawning = no double billing, full context | Validated Phase 2 |
| npm distribution | Follow GSD pattern exactly for ecosystem consistency | Validated Phase 1 |
| All 3 domains in v1 | Complete feature parity with mlforge from day one | Validated Phase 4 |
| `.ml/` state directory | Separate from `.planning/` to allow both GSD and gsd-ml in same project | Validated Phase 2 |
| JSON config (not TOML) | Native JS parsing, Claude Code can read/write directly, simpler | Validated Phase 2 |
| train.py outputs JSON to stdout | Simplest metric contract between training script and Claude Code | Validated Phase 2 |
| Git branch per run, commit per keep | Proven pattern from mlforge; atomic state management | Validated Phase 2 |
| Drop swarm mode for v1 | Subprocess-based parallelism doesn't translate; redesign later if needed | Validated v1.0 |
| No Optuna | Claude Code iterates manually; HPO framework unnecessary | Validated Phase 2 |
| __PLACEHOLDER__ constants | Static template with string replacement instead of Jinja2 | Validated Phase 2 |
| Guardrails read start_time from config.json | Survives context resets unlike in-memory timers | Validated Phase 2 |

---
*Last updated: 2026-03-23 after v1.0 milestone*
