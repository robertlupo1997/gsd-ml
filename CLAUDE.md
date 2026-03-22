# gsd-ml

Claude Code native autonomous ML research tool. Distributed as an npm package following GSD (get-shit-done-cc) patterns.

## Planning

All project context is in `.planning/`:
- `PROJECT.md` — what this is, core value, constraints, key decisions
- `REQUIREMENTS.md` — 48 v1 requirements with traceability
- `ROADMAP.md` — 6 phases, success criteria
- `STATE.md` — current progress, session history
- `config.json` — GSD workflow configuration

Use `/gsd:plan-phase` to plan the next phase, `/gsd:execute-phase` to build it.

## Architecture

gsd-ml is a redesign of **mlforge** (`/home/tlupo/AutoML/src/mlforge/`). Instead of a Python CLI that spawns `claude -p` subprocesses, Claude Code IS the ML researcher — it edits train.py, runs it via Bash, parses metrics, and makes keep/revert decisions directly.

**Distribution:** npm package (like get-shit-done-cc) that installs skills, workflows, references, and templates into `~/.claude/`. Python ML utilities ship as a separate pip package (`gsd_ml`).

**Key pattern:** Skills → Workflows → Claude Code executes with native tools (Read/Write/Edit/Bash/git)

## Source Code to Port

~80% of mlforge's Python utilities carry over. Source location: `/home/tlupo/AutoML/src/mlforge/`

| gsd_ml module | Source (mlforge path) | Adaptation |
|---------------|----------------------|------------|
| profiler.py | mlforge/profiler.py | Inline leakage check, change imports |
| state.py | mlforge/state.py | Change imports only |
| checkpoint.py | mlforge/checkpoint.py | Change imports only |
| guardrails.py | mlforge/guardrails.py | JSON config instead of Config dataclass |
| diagnostics.py | mlforge/intelligence/diagnostics.py | None (pure numpy) |
| drafts.py | mlforge/intelligence/drafts.py | None (pure data) |
| stagnation.py | mlforge/intelligence/stagnation.py | Remove GitPython dep |
| results.py | mlforge/results.py | Change imports |
| journal.py | mlforge/journal.py | Remove GitPython from get_last_diff |
| retrospective.py | mlforge/retrospective.py | Change imports |
| export.py | mlforge/export.py | Change imports |
| baselines/tabular.py | mlforge/tabular/baselines.py | None |
| baselines/deeplearning.py | mlforge/deeplearning/baselines.py | None |
| baselines/finetuning.py | mlforge/finetuning/baselines.py | None |
| prepare/tabular.py | mlforge/tabular/prepare.py | None |
| prepare/deeplearning.py | mlforge/deeplearning/prepare.py | None |
| prepare/finetuning.py | mlforge/finetuning/prepare.py | None |

**Templates to port** (from `mlforge/templates/`):
- `tabular_train.py.j2` → `templates/train-tabular.py` (de-Jinja2, make static)
- `dl_train.py.j2` → `templates/train-dl.py`
- `ft_train.py.j2` → `templates/train-ft.py`

**Dropped from mlforge** (subprocess-specific): engine.py, cli.py, swarm/, hooks.py, progress.py, plugins.py, templates/*.j2 (Jinja2 templates replaced by static files + workflow instructions)

## GSD Pattern Reference

Follow exactly how GSD (get-shit-done-cc) works:
- `~/.claude/get-shit-done/` — installed package location, study for patterns
- `~/.claude/commands/gsd/` — skill files (YAML frontmatter + XML execution blocks)
- `~/.claude/get-shit-done/workflows/` — workflow .md files
- `~/.claude/get-shit-done/templates/` — output format templates
- `~/.claude/get-shit-done/references/` — decision guides
- `~/.claude/get-shit-done/bin/gsd-tools.cjs` — JS CLI tooling
