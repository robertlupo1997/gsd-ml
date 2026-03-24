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
