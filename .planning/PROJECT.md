# gsd-ml

## What This Is

A Claude Code native autonomous ML research tool, distributed as an npm package following the GSD (get-shit-done-cc) pattern. Users invoke `/gsd:ml dataset.csv target_column` and Claude Code itself becomes the ML researcher -- profiling data, writing training scripts, running experiments, tracking results via git, and iterating until budget is exhausted. Supports tabular ML, deep learning, and LLM fine-tuning.

## Core Value

Claude Code autonomously runs structured ML experiments with full guardrails, git state tracking, and crash recovery -- without spawning subprocess agents or double-billing API costs.

## Requirements

### Validated

(None yet -- ship to validate)

### Active

- [ ] Claude Code can profile a dataset and auto-detect task type, metric, and direction
- [ ] Claude Code scaffolds a `.ml/` experiment directory with frozen prepare.py and mutable train.py
- [ ] Claude Code runs the experiment loop: edit train.py, run it, parse metrics, keep/revert via git
- [ ] Guardrails enforce cost, time, experiment count, and disk space limits
- [ ] Diagnostics analyze where the model fails and inject findings into next iteration
- [ ] Multi-draft phase explores 3-5 diverse initial solutions before linear iteration
- [ ] Stagnation detection branches to new model family after N consecutive reverts
- [ ] Checkpoint/resume survives context resets and session restarts
- [ ] Tabular domain works (sklearn, XGBoost, LightGBM, Optuna)
- [ ] Deep learning domain works (PyTorch, timm, transformers)
- [ ] Fine-tuning domain works (peft, trl, LoRA, QLoRA)
- [ ] npm package installs skills, workflows, references, templates into ~/.claude/
- [ ] Python utilities installable via pip/uv for ML-specific operations
- [ ] `/gsd:ml-status` shows past experiment runs
- [ ] `/gsd:ml-resume` resumes an interrupted experiment
- [ ] `/gsd:ml-clean` removes old experiment artifacts

### Out of Scope

- Web UI or dashboard -- CLI/Claude Code only, terminal output and log files
- Cloud orchestration (AWS/GCP job submission) -- local-first, single machine
- Swarm/multi-agent mode -- dropped from mlforge; may revisit in v2
- Real-time data ingestion -- batch input (CSV, Parquet, JSON, JSONL)
- Building LLMs from scratch -- fine-tuning existing models only
- Replacing GSD -- gsd-ml is a domain-specific companion, not a fork

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
| Claude Code does everything | No subprocess spawning = no double billing, full context | -- Pending |
| npm distribution | Follow GSD pattern exactly for ecosystem consistency | -- Pending |
| All 3 domains in v1 | Complete feature parity with mlforge from day one | -- Pending |
| `.ml/` state directory | Separate from `.planning/` to allow both GSD and gsd-ml in same project | -- Pending |
| JSON config (not TOML) | Native JS parsing, Claude Code can read/write directly, simpler | -- Pending |
| train.py outputs JSON to stdout | Simplest metric contract between training script and Claude Code | -- Pending |
| Git branch per run, commit per keep | Proven pattern from mlforge; atomic state management | -- Pending |
| Drop swarm mode for v1 | Subprocess-based parallelism doesn't translate; redesign later if needed | -- Pending |

---
*Last updated: 2026-03-22 after initial project definition*
