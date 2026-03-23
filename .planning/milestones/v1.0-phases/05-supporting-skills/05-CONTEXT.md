# Phase 5: Supporting Skills - Context

**Gathered:** 2026-03-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Four standalone Claude Code skills that operate on `.ml/` experiment state: status reporting (`/gsd:ml-status`), resume from checkpoint (`/gsd:ml-resume`), cleanup (`/gsd:ml-clean`), and standalone diagnostics (`/gsd:ml-diagnose`). Each skill gets its own skill file (YAML + XML) pointing to either inline logic or a workflow .md file.

</domain>

<decisions>
## Implementation Decisions

### Status output (/gsd:ml-status)
- Default view: summary table printed to terminal with columns: run ID, domain, metric name, best value, #experiments, keeps/reverts, cost, start time, duration, time/experiment
- `--detail <run_id>` flag for full markdown report on a specific run
- Detail view includes ASCII chart showing metric trajectory across experiments
- Scoped to current `.ml/` directory only (no parent/sibling scanning)
- Data sourced from `.ml/results.jsonl` and `.ml/checkpoint.json`

### Resume behavior (/gsd:ml-resume)
- Auto-detect last run from `.ml/checkpoint.json` by default
- `--run <id>` flag to resume a specific older run
- If budget exhausted: warn and offer to extend with additional experiments
- Auto-checkout the correct `ml/run-{id}` git branch on resume
- Trust the checkpoint (atomic write-then-rename guarantees consistency) — no re-run verification

### Clean scope (/gsd:ml-clean)
- Default: remove `.ml/` directory only (git branches/tags preserved)
- `--branches` flag to also delete `ml/run-*` branches and `ml-best-*` tags
- Before deleting: show what will be removed (files, sizes), require confirmation
- `--force` flag skips confirmation for scripting use
- Offer to copy best model artifact from `.ml/artifacts/` to `./model/` before wiping

### Diagnose standalone (/gsd:ml-diagnose)
- Analyze best model from last run (checkout `best_commit` from checkpoint)
- Requires `.ml/` directory (reads task type, metric, data location from `config.json`)
- Output: formatted markdown printed to terminal (worst predictions, bias, feature correlations, confused classes)
- Includes "Suggested Actions" section with actionable hints based on findings (e.g., "High bias on class X -> try class weighting")

### Claude's Discretion
- Exact ASCII chart library/approach for metric trajectory
- Table formatting library (or plain string formatting)
- How to structure the "extend budget" prompt in resume
- Whether diagnose temporarily checks out best_commit or runs in detached HEAD

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `checkpoint.py`: `save_checkpoint()` / `load_checkpoint()` with atomic write-then-rename — resume reads this directly
- `state.py`: `SessionState` dataclass with experiment_count, best_metric, best_commit, run_id, cost, keeps/reverts, tried_families
- `results.py`: `ResultTracker` with JSONL persistence, `get_best()`, `get_summary()`, filter by status
- `journal.py`: `JournalEntry` with hypothesis/outcome/metric per experiment, markdown rendering
- `diagnostics.py`: `diagnose_regression()` / `diagnose_classification()` — pure numpy, ready for standalone use
- `guardrails.py`: Budget enforcement — resume can re-read guardrail config to offer budget extension

### Established Patterns
- Skill file: YAML frontmatter + XML body (see `ml.md` for reference)
- Workflow files live in `~/.claude/gsd-ml/workflows/`
- Python utilities called via `python -c "from gsd_ml.X import Y; ..."` from Bash
- `.ml/config.json` stores run configuration (domain, metric, direction, dataset path, guardrail limits)

### Integration Points
- Skill files install to `~/.claude/commands/gsd-ml/` (ml-status.md, ml-resume.md, ml-clean.md, ml-diagnose.md)
- Resume re-enters the experiment loop defined in `ml-run.md` workflow
- Status reads `.ml/results.jsonl` and `.ml/checkpoint.json`
- Clean removes `.ml/` directory and optionally git branches matching `ml/run-*` pattern
- Diagnose checkouts `best_commit` from `SessionState.best_commit`

</code_context>

<specifics>
## Specific Ideas

No specific requirements — open to standard approaches. User wants recommendations-first approach with sensible defaults.

</specifics>

<deferred>
## Deferred Ideas

- AutoML integration (auto-sklearn, FLAML, etc.) — potential future phase for automated model/hyperparameter search beyond Claude Code's manual iteration

</deferred>

---

*Phase: 05-supporting-skills*
*Context gathered: 2026-03-22*
