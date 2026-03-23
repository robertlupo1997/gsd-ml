# Phase 5: Supporting Skills - Research

**Researched:** 2026-03-22
**Domain:** Claude Code skill files (YAML+XML) with workflow .md orchestration
**Confidence:** HIGH

## Summary

Phase 5 creates four standalone Claude Code skills that operate on the `.ml/` experiment state: `/gsd:ml-status`, `/gsd:ml-resume`, `/gsd:ml-clean`, and `/gsd:ml-diagnose`. Each skill is a YAML frontmatter + XML body file installed to `~/.claude/commands/gsd-ml/`, optionally pointing to a workflow .md file for complex logic.

All four skills consume existing Python modules (checkpoint.py, state.py, results.py, diagnostics.py, guardrails.py, journal.py) and existing `.ml/` state files (checkpoint.json, results.jsonl, config.json, experiments.jsonl). No new Python modules are needed. The work is primarily creating skill files and workflow files with correct orchestration logic.

**Primary recommendation:** Create 4 skill files and 2-3 workflow files. Status, clean, and diagnose are self-contained enough to be inline in the skill file or a short workflow. Resume is complex (re-enters experiment loop) and should reference the existing ml-run.md workflow with a "resume mode" entry point.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **Status output:** Summary table with columns: run ID, domain, metric name, best value, #experiments, keeps/reverts, cost, start time, duration, time/experiment. `--detail <run_id>` for full markdown report with ASCII metric trajectory chart. Scoped to current `.ml/` only. Data from results.jsonl and checkpoint.json.
- **Resume behavior:** Auto-detect last run from checkpoint.json. `--run <id>` for specific run. Warn on budget exhaustion with offer to extend. Auto-checkout `ml/run-{id}` branch. Trust checkpoint (no re-run verification).
- **Clean scope:** Default removes `.ml/` only. `--branches` also deletes `ml/run-*` branches and `ml-best-*` tags. Show what will be removed before deleting, require confirmation. `--force` skips confirmation. Offer to copy best model artifact to `./model/` before wiping.
- **Diagnose standalone:** Analyze best model from last run (checkout best_commit). Requires `.ml/` directory. Output: formatted markdown (worst predictions, bias, correlations, confused classes). Includes "Suggested Actions" section with actionable hints.

### Claude's Discretion
- Exact ASCII chart library/approach for metric trajectory
- Table formatting library (or plain string formatting)
- How to structure the "extend budget" prompt in resume
- Whether diagnose temporarily checks out best_commit or runs in detached HEAD

### Deferred Ideas (OUT OF SCOPE)
- AutoML integration (auto-sklearn, FLAML, etc.)
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| STATE-02 | Resume from checkpoint after context reset or crash | Resume skill reads checkpoint.json via load_checkpoint(), restores SessionState, checks out correct branch, re-enters experiment loop at Phase 3 of ml-run.md |
| SKILL-01 | /gsd:ml-status shows past experiment runs | Status skill reads results.jsonl via ResultsTracker and checkpoint.json via load_checkpoint(), formats summary table and optional detail view |
| SKILL-02 | /gsd:ml-resume loads checkpoint and re-enters experiment loop | Resume skill loads checkpoint, reads config.json for guardrails/domain, checks out ml/run-{id} branch, then follows ml-run.md Phase 3 loop |
| SKILL-03 | /gsd:ml-clean removes .ml/ directories and experiment branches | Clean skill lists .ml/ contents, optionally lists ml/run-* branches, confirms with user, removes files/branches |
| SKILL-04 | /gsd:ml-diagnose runs diagnostics on current model standalone | Diagnose skill reads config.json for task type, checks out best_commit, runs diagnose_regression/diagnose_classification, formats output with suggested actions |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| gsd_ml.checkpoint | - | load_checkpoint() for reading SessionState | Already built in Phase 1 |
| gsd_ml.results | - | ResultsTracker for reading results.jsonl | Already built in Phase 1 |
| gsd_ml.state | - | SessionState dataclass | Already built in Phase 1 |
| gsd_ml.diagnostics | - | diagnose_regression/classification | Already built in Phase 1 |
| gsd_ml.guardrails | - | ResourceGuardrails for budget checking | Already built in Phase 1 |
| gsd_ml.journal | - | load_journal/render_journal_markdown | Already built in Phase 1 |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Plain Python string formatting | stdlib | Table and chart rendering | All output formatting -- no external dependencies needed |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Plain string formatting | rich/tabulate | Adds dependency for terminal formatting; not worth it since Claude Code controls output |
| Manual ASCII chart | asciichartpy | Small lib but adds pip dependency; simple loop with bar chars is sufficient |

**No new packages required.** All four skills use existing gsd_ml modules and Python stdlib.

## Architecture Patterns

### Skill File Structure
Each skill is a `.md` file in `commands/gsd-ml/` with YAML frontmatter + XML body, following the established pattern from `ml.md`:

```yaml
---
name: gsd:ml-status
description: Show experiment run status and metrics
argument-hint: "[--detail <run_id>]"
allowed-tools: [Read, Bash, Glob]
---
<objective>...</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-status.md</execution_context>
<context>Arguments: $ARGUMENTS</context>
<process>...</process>
```

### Recommended Project Structure
```
commands/gsd-ml/
  ml.md              # existing - main experiment skill
  ml-status.md       # new - status reporting
  ml-resume.md       # new - resume from checkpoint
  ml-clean.md        # new - cleanup
  ml-diagnose.md     # new - standalone diagnostics

gsd-ml/workflows/
  ml-run.md          # existing - main experiment workflow
  ml-status.md       # new - status reporting workflow
  ml-resume.md       # new - resume workflow (thin: loads state, re-enters ml-run.md Phase 3)
  ml-clean.md        # new - cleanup workflow
  ml-diagnose.md     # new - diagnostics workflow
```

### Pattern 1: Skill as Thin Shell, Workflow Does Work
**What:** Skill file contains YAML metadata + XML that points to a workflow .md file. The workflow contains step-by-step instructions for Claude Code.
**When to use:** All four skills follow this pattern. Even simple skills benefit from having the logic in a separate workflow file for maintainability.
**Example:**
```yaml
# commands/gsd-ml/ml-status.md
---
name: gsd:ml-status
description: Show experiment run status and metrics
argument-hint: "[--detail <run_id>]"
allowed-tools: [Read, Bash, Glob]
---
<objective>Display experiment status for runs in the current .ml/ directory.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-status.md</execution_context>
<context>Arguments: $ARGUMENTS</context>
<process>Follow the ml-status workflow step by step.</process>
```

### Pattern 2: Resume Re-Enters Existing Workflow
**What:** The resume skill does NOT duplicate the experiment loop. It loads state from checkpoint, sets up the environment (branch checkout, variable restoration), then tells Claude to follow ml-run.md starting at Phase 3.
**When to use:** For resume specifically -- avoids duplicating the experiment loop logic.
**Key detail:** The resume workflow must:
1. Load checkpoint.json via `load_checkpoint()`
2. Read config.json for domain, metric, direction, budget, start_time
3. Checkout the correct `ml/run-{run_id}` branch
4. Reconstruct all loop variables from SessionState fields
5. Instruct Claude to follow ml-run.md Phase 3 (Experiment Loop) with these restored variables

### Pattern 3: Python One-Liners via Bash
**What:** All Python module calls are done via `python -c "..."` from Bash, consistent with the ml-run.md workflow pattern.
**When to use:** Every time a skill needs to call gsd_ml modules.
**Example:**
```bash
python -c "
import json
from pathlib import Path
from gsd_ml.checkpoint import load_checkpoint
from gsd_ml.results import ResultsTracker

state = load_checkpoint(Path('.ml'))
tracker = ResultsTracker(Path('.ml/results.jsonl'))
summary = tracker.summary()
print(json.dumps({'state': state.__dict__ if state else None, 'summary': summary}))
"
```

### Anti-Patterns to Avoid
- **Duplicating experiment loop in resume workflow:** Resume should reference ml-run.md Phase 3, not copy it. Otherwise changes to the loop require updating two files.
- **Reading raw JSON files manually:** Always use the Python modules (load_checkpoint, ResultsTracker) which handle schema versioning and error cases.
- **Complex Python scripts in workflow files:** Keep Python one-liners focused. If logic gets complex, it belongs in a gsd_ml module, not inline.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Checkpoint loading | Manual JSON parsing | `load_checkpoint()` from checkpoint.py | Handles schema versioning, missing fields, corrupt JSON |
| Results querying | Manual JSONL parsing | `ResultsTracker` from results.py | Handles filtering, summary stats, best-finding with direction |
| Diagnostics computation | Inline numpy code | `diagnose_regression/classification` from diagnostics.py | Handles edge cases, per-class stats, confused pairs |
| Journal rendering | Manual markdown generation | `render_journal_markdown()` from journal.py | Consistent formatting with the loop output |
| Budget checking | Manual time/count comparison | Read config.json fields directly | start_time is already persisted in config.json |

**Key insight:** All the heavy lifting is already in gsd_ml Python modules from Phase 1. The skills are orchestration layers that read state, call modules, and format output.

## Common Pitfalls

### Pitfall 1: Resume Branch Mismatch
**What goes wrong:** Resume loads checkpoint but doesn't checkout the correct git branch, causing commits to land on wrong branch.
**Why it happens:** The run_id in checkpoint maps to a branch `ml/run-{run_id}`, but if user is on main or another branch, resume must switch.
**How to avoid:** Resume workflow MUST `git checkout ml/run-{run_id}` before re-entering the loop. Verify branch exists first with `git branch --list`.
**Warning signs:** Commits appearing on main branch instead of experiment branch.

### Pitfall 2: Budget Extension Resets start_time
**What goes wrong:** When extending budget on resume, if start_time is updated, elapsed time calculation resets and the original time budget appears unused.
**Why it happens:** Confusion between "extend experiment count" vs "extend time budget" vs "start fresh timer."
**How to avoid:** On budget extension, only modify `budget_experiments` (add N more) or `budget_minutes` (add N more). Never reset `start_time`. The guardrail check uses `now - start_time < budget_minutes * 60`, so increasing budget_minutes gives more time.

### Pitfall 3: Clean Deletes Before Confirmation
**What goes wrong:** Running `rm -rf .ml/` before showing the user what will be deleted.
**Why it happens:** Skipping the preview step.
**How to avoid:** Always: 1) scan and display, 2) ask confirmation (unless --force), 3) then delete. The preview should show file count, total size, and list of branches if --branches.

### Pitfall 4: Diagnose Modifies Working Tree
**What goes wrong:** Checking out best_commit changes the working tree, and if diagnose fails, the user is left on wrong commit.
**Why it happens:** `git checkout {best_commit}` puts repo in detached HEAD state.
**How to avoid:** Save current branch/HEAD before checkout, run diagnostics, then restore. Use pattern: `current=$(git rev-parse --abbrev-ref HEAD)` ... do work ... `git checkout $current`.

### Pitfall 5: Status Fails on Empty .ml/
**What goes wrong:** Status skill crashes when .ml/ exists but has no results.jsonl or checkpoint.json.
**Why it happens:** ResultsTracker and load_checkpoint handle missing files gracefully (empty list / None), but the formatting code may not expect empty data.
**How to avoid:** Check for None/empty returns before formatting. Display "No experiments recorded yet" for empty state.

### Pitfall 6: Multiple Run IDs in Single .ml/
**What goes wrong:** Status/resume assume one run per .ml/ directory, but stagnation branching creates explore branches with the same .ml/ state.
**Why it happens:** The .ml/ directory tracks a single logical run (with potential stagnation branches). checkpoint.json always has the latest run_id.
**How to avoid:** Status shows the current run from checkpoint.json. If --detail is used with a specific run_id, it would need to filter results.jsonl by timestamp ranges. For v1, scope to current run only (consistent with CONTEXT.md "scoped to current .ml/ directory only").

## Code Examples

### Loading State for Status
```python
# Source: existing gsd_ml modules
import json
from pathlib import Path
from gsd_ml.checkpoint import load_checkpoint
from gsd_ml.results import ResultsTracker

ml_dir = Path('.ml')
state = load_checkpoint(ml_dir)  # Returns SessionState or None
config = json.loads((ml_dir / 'config.json').read_text())
tracker = ResultsTracker(ml_dir / 'results.jsonl')
summary = tracker.summary()

# State fields: run_id, experiment_count, best_metric, best_commit,
#   total_keeps, total_reverts, cost_spent_usd, task, baselines,
#   consecutive_reverts, tried_families
```

### ASCII Metric Trajectory Chart
```python
# Simple bar chart approach -- no dependencies
def ascii_chart(values, labels, width=40):
    """Render a simple horizontal bar chart."""
    if not values:
        return "No data"
    max_val = max(abs(v) for v in values if v is not None)
    lines = []
    for label, val in zip(labels, values):
        if val is None:
            bar = "  [crashed]"
        else:
            bar_len = int((val / max_val) * width) if max_val > 0 else 0
            bar = "#" * bar_len + f" {val:.4f}"
        lines.append(f"  {label:>4} | {bar}")
    return "\n".join(lines)
```

### Resume: Restoring Loop State
```python
import json
from pathlib import Path
from gsd_ml.checkpoint import load_checkpoint

state = load_checkpoint(Path('.ml'))
config = json.loads(Path('.ml/config.json').read_text())

# These are the variables the experiment loop needs:
print(json.dumps({
    'run_id': state.run_id,
    'experiment_count': state.experiment_count,
    'best_metric': state.best_metric,
    'best_commit': state.best_commit,
    'total_keeps': state.total_keeps,
    'total_reverts': state.total_reverts,
    'consecutive_reverts': state.consecutive_reverts,
    'tried_families': state.tried_families,
    'task': state.task,
    'domain': config.get('domain', 'tabular'),
    'metric': config.get('metric'),
    'direction': config.get('direction'),
    'budget_experiments': config.get('budget_experiments'),
    'budget_minutes': config.get('budget_minutes'),
}))
```

### Clean: Preview and Delete
```bash
# Preview
echo "Files in .ml/:"
du -sh .ml/ 2>/dev/null
find .ml/ -type f | wc -l
echo "---"

# Branch preview (only with --branches)
git branch --list 'ml/run-*'
git tag --list 'ml-best-*'
```

### Diagnose: Checkout, Run, Restore
```bash
# Save current position
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
BEST_COMMIT=$(python -c "
from gsd_ml.checkpoint import load_checkpoint
from pathlib import Path
state = load_checkpoint(Path('.ml'))
print(state.best_commit if state and state.best_commit else '')
")

if [ -n "$BEST_COMMIT" ]; then
    git checkout "$BEST_COMMIT" -- .ml/train.py
    # Run train.py in eval mode to get predictions
    cd .ml && python train.py
    # Run diagnostics
    python -c "
import json, pandas as pd
from pathlib import Path
from gsd_ml.diagnostics import diagnose_regression, diagnose_classification
preds = pd.read_csv('predictions.csv')
config = json.loads(Path('config.json').read_text())
task = config['task']
if task in ('classification', 'image_classification', 'text_classification'):
    diag = diagnose_classification(preds['y_true'].values, preds['y_pred'].values)
else:
    diag = diagnose_regression(preds['y_true'].values, preds['y_pred'].values)
print(json.dumps(diag, indent=2, default=str))
"
    # Restore
    git checkout "$CURRENT_BRANCH" -- .ml/train.py
fi
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Jinja2 templates for skills | Static markdown skill files (YAML+XML) | Phase 1 | Skills are readable, no template engine needed |
| GitPython for branch ops | subprocess.run with git CLI | Phase 1 | No GitPython dependency |
| Complex CLI with argparse | Claude Code skills with $ARGUMENTS | Phase 1 | Natural language argument parsing by Claude |

**No deprecated patterns to worry about.** All underlying modules are current.

## Open Questions

1. **How should resume handle budget_minutes elapsed during previous session?**
   - What we know: start_time is stored in config.json as ISO timestamp. If the user resumes 2 hours later and the original budget was 60 minutes, the time budget is already exhausted.
   - What's unclear: Should resume recalculate remaining time, or should it simply warn and offer to extend?
   - Recommendation: On resume, check if time budget is already exhausted. If so, warn user and offer to increase budget_minutes in config.json. This is consistent with the "warn and offer to extend" behavior from CONTEXT.md.

2. **How should diagnose handle FT/DL models that need GPU?**
   - What we know: diagnose_regression/classification are pure numpy and work on CPU. But generating predictions.csv from train.py may require GPU for DL/FT models.
   - What's unclear: Should diagnose attempt to re-run train.py, or only work if predictions.csv already exists?
   - Recommendation: Diagnose should first check if `.ml/predictions.csv` exists from the last run. If it does, use it directly. If not, attempt to run train.py with the best model to generate predictions. This avoids mandatory GPU requirement for the diagnostics skill itself.

3. **Should status support multiple .ml/ directories (past runs)?**
   - What we know: CONTEXT.md says "scoped to current .ml/ directory only."
   - Recommendation: Only show current .ml/ directory. Users who want history across runs can look at git tags (ml-best-*).

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest |
| Config file | python/pyproject.toml (assumed) |
| Quick run command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` |
| Full suite command | `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| STATE-02 | Resume loads checkpoint and re-enters loop | integration | Manual verification -- resume re-enters ml-run.md workflow via Claude Code | manual-only |
| SKILL-01 | /gsd:ml-status shows past runs | integration | Manual verification -- skill file invoked by Claude Code | manual-only |
| SKILL-02 | /gsd:ml-resume loads checkpoint | integration | Manual verification -- skill file invoked by Claude Code | manual-only |
| SKILL-03 | /gsd:ml-clean removes .ml/ and branches | integration | Manual verification -- skill file invoked by Claude Code | manual-only |
| SKILL-04 | /gsd:ml-diagnose runs standalone diagnostics | integration | Manual verification -- skill file invoked by Claude Code | manual-only |

**Note:** All phase requirements are skill files (markdown) and workflow files (markdown) that are executed by Claude Code as the runtime. They cannot be unit tested in the traditional sense -- they are tested by invoking the skill commands in Claude Code. The underlying Python modules (checkpoint, results, diagnostics) are already fully tested from Phase 1. The new code is orchestration logic in markdown workflow files.

### Sampling Rate
- **Per task commit:** `cd /home/tlupo/gsd-ml && python -m pytest python/tests/ -x -q` (verify no regressions in Python modules)
- **Per wave merge:** Full suite
- **Phase gate:** Manual invocation of each skill command to verify behavior

### Wave 0 Gaps
None -- existing test infrastructure covers the Python modules. Skill/workflow files are validated by manual invocation.

## Sources

### Primary (HIGH confidence)
- Direct code inspection of: checkpoint.py, state.py, results.py, diagnostics.py, guardrails.py, journal.py, export.py, retrospective.py
- Direct code inspection of: commands/gsd-ml/ml.md (skill file pattern), gsd-ml/workflows/ml-run.md (workflow pattern)
- Direct code inspection of: ~/.claude/commands/gsd/health.md (GSD skill file reference pattern)

### Secondary (MEDIUM confidence)
- CONTEXT.md decisions (user-provided, authoritative for this project)

### Tertiary (LOW confidence)
- None

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all modules exist and are tested, inspected source code directly
- Architecture: HIGH - skill file and workflow patterns are established, followed existing ml.md/ml-run.md pattern
- Pitfalls: HIGH - identified from direct inspection of state management, git operations, and edge cases in existing code

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- no external dependencies changing)
