# Phase 3: Intelligence Layer - Research

**Researched:** 2026-03-22
**Domain:** ML experiment intelligence (baselines, diagnostics, stagnation, multi-draft)
**Confidence:** HIGH

## Summary

Phase 3 adds intelligence features to the existing experiment loop from Phase 2. The good news: all Python utilities are already ported and tested (54 tests passing). The work is primarily **workflow integration** -- wiring existing `gsd_ml` modules into `ml-run.md` at the right points in the experiment lifecycle.

The phase breaks into four distinct capabilities: (1) baseline computation + gating, (2) post-experiment diagnostics injection, (3) stagnation detection + branching, and (4) multi-draft initial exploration. These are layered on top of the existing profile -> scaffold -> loop -> finalize workflow. Baselines are already partially scaffolded in the workflow (Step 2.7 computes them) but not yet enforced as a gate. The other three features have no workflow presence yet.

**Primary recommendation:** Integrate all four intelligence features into `ml-run.md` as additions to existing workflow phases. No new Python code needed -- only workflow markdown changes and minor adjustments to how the experiment loop makes decisions.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| INTEL-01 | Compute baselines (naive strategies) before experimentation | `baselines/tabular.py` already called in workflow Step 2.7; needs baseline results stored in config/checkpoint |
| INTEL-02 | Baseline gate: model must beat baselines to be kept | `passes_baseline_gate()` exists in `baselines/tabular.py`; needs integration into Step 3.4 keep/revert decision |
| INTEL-03 | Diagnostics: analyze worst predictions, bias, feature-error correlations | `diagnostics.py` has `diagnose_regression()` and `diagnose_classification()`; needs call after each experiment |
| INTEL-04 | Inject diagnostics into next iteration prompt | Diagnostics output needs to be saved to a file and read before Step 3.2 (edit train.py) |
| INTEL-05 | Multi-draft phase: 3-5 diverse initial solutions, pick best | `drafts.py` has `ALGORITHM_FAMILIES`, `DraftResult`, `select_best_draft()`; needs new workflow phase between scaffold and loop |
| INTEL-06 | Stagnation detection: N consecutive reverts triggers model family switch | `stagnation.py` has `check_stagnation()` with configurable threshold; needs check in loop after revert |
| INTEL-07 | Branch-on-stagnation: git branch from best-ever, try different family | `trigger_stagnation_branch()` exists; needs workflow step to create branch and switch model family |
</phase_requirements>

## Standard Stack

### Core (Already Ported -- Phase 1)

| Module | Location | Purpose | Tests |
|--------|----------|---------|-------|
| `baselines/tabular.py` | `gsd_ml.baselines.tabular` | Compute dummy baselines, baseline gate check | Passing (12 tests) |
| `diagnostics.py` | `gsd_ml.diagnostics` | Regression/classification error analysis | Passing (15 tests) |
| `drafts.py` | `gsd_ml.drafts` | Algorithm families, DraftResult, select_best_draft | Passing (13 tests) |
| `stagnation.py` | `gsd_ml.stagnation` | check_stagnation, trigger_stagnation_branch | Passing (14 tests) |

### Supporting (Already in Use)

| Module | Purpose | Relevance |
|--------|---------|-----------|
| `state.py` | `SessionState` dataclass | Already has `baselines`, `tried_families`, `consecutive_reverts` fields |
| `checkpoint.py` | Save/load state | Baselines and tried_families persist across checkpoints |
| `guardrails.py` | `DeviationHandler` | Keep/revert decision needs baseline gate added |
| `results.py` | `ResultsTracker` | Track draft-phase results separately |

### No New Dependencies

All intelligence features use modules already installed: numpy, sklearn, pandas. No new pip packages needed.

## Architecture Patterns

### Integration Points in ml-run.md

The existing workflow has 4 phases. Intelligence features slot in at specific points:

```
Phase 1: Profile Dataset          (unchanged)
Phase 2: Scaffold .ml/ Directory
  Step 2.7: Compute Baselines     <- INTEL-01: save baselines to checkpoint
  NEW Step 2.8: Multi-Draft Phase <- INTEL-05: run 3-5 diverse drafts
  Step 2.9: Create Git Branch     (renumber)
  Step 2.10: Initial Commit       (renumber)
Phase 3: Experiment Loop
  Step 3.2: Edit train.py         <- INTEL-04: read diagnostics before editing
  Step 3.4: Keep/Revert Decision  <- INTEL-02: add baseline gate
  NEW Step 3.5a: Run Diagnostics  <- INTEL-03: after each experiment
  NEW Step 3.5b: Stagnation Check <- INTEL-06/07: after revert, check + branch
  Step 3.5: Record Results        (renumber)
Phase 4: Finalize                 (unchanged)
```

### Pattern 1: Baseline Gate Integration

**What:** After the DeviationHandler says "keep", check if the metric also beats all baselines. If not, treat as "revert" instead.

**How it works in the workflow:**
```python
# In Step 3.4, after DeviationHandler returns "keep":
from gsd_ml.baselines.tabular import passes_baseline_gate
baselines = json.loads(Path('.ml/config.json').read_text()).get('baselines', {})
if not passes_baseline_gate(metric_value, baselines, direction):
    decision = "revert"  # Downgrade: beats previous best but not baselines
```

**Key detail:** Baselines must be stored in `.ml/config.json` (or `checkpoint.json`) during scaffold phase so they survive context resets. The `SessionState` dataclass already has a `baselines` field.

### Pattern 2: Diagnostics Injection

**What:** After each experiment run, analyze predictions and write diagnostics to `.ml/diagnostics.json`. Before the next edit, Claude reads this file to inform its changes.

**How it works:**
1. train.py already saves `predictions.csv` (y_true, y_pred columns) -- this is in the template
2. After train.py runs, workflow calls `diagnose_regression()` or `diagnose_classification()`
3. Output saved to `.ml/diagnostics.json`
4. Before Step 3.2 (edit train.py), workflow instructs Claude to read `.ml/diagnostics.json` and use findings

**Key detail:** Diagnostics run on test set predictions from `predictions.csv`. For classification, `diagnose_classification()` needs y_true and y_pred arrays. For regression with feature correlations, it also needs X and feature_names -- these require the prepare module.

### Pattern 3: Multi-Draft Exploration

**What:** Before the main iteration loop, try 3-5 diverse model families. Each draft gets one shot. The best draft becomes the starting point for iteration.

**How it works:**
1. Get families from `drafts.get_families_for_domain("tabular")` -- returns linear, random_forest, xgboost, lightgbm, svm
2. For each family, modify train.py to use that family's model class
3. Run train.py, record result as `DraftResult`
4. After all drafts, `select_best_draft()` picks the winner
5. Checkout the best draft's commit, continue to iteration loop

**Key detail:** Drafts should be recorded with status "draft-keep"/"draft-discard" (not "keep"/"revert") to distinguish from iteration experiments. The `DraftResult` dataclass already has this status field.

**Git flow for drafts:**
- Each draft commits its train.py changes
- After all drafts run, checkout the best draft's commit
- Continue iteration from that point

### Pattern 4: Stagnation Branch

**What:** After N consecutive reverts, create a git branch from best-ever commit and try a different model family.

**How it works:**
1. After each revert, check `state.consecutive_reverts >= threshold` (default 3)
2. If stagnated, pick an untried family from `drafts.get_families_for_domain()`
3. Call `trigger_stagnation_branch()` to create `explore-{family}` branch
4. Modify train.py for the new family
5. Continue iterating on the new branch
6. At finalize, compare branches and keep the best

**Key detail:** `SessionState.tried_families` tracks which families have been attempted. `SessionState.consecutive_reverts` resets to 0 on keep or on stagnation branch. The workflow needs to handle the case where ALL families have been tried (then just continue iterating).

### Anti-Patterns to Avoid

- **Modifying DeviationHandler for baseline gate:** The baseline gate is a workflow-level concern, not a DeviationHandler concern. DeviationHandler compares against best_metric; baseline gate is a separate check. Keep them separate.
- **Running diagnostics inside train.py:** Diagnostics should be run by the workflow after train.py, not inside train.py itself. train.py just saves predictions.csv.
- **Storing diagnostics in checkpoint:** Diagnostics are ephemeral per-experiment. Save to `.ml/diagnostics.json` (overwritten each time), not in checkpoint.
- **Committing draft experiments as regular keeps:** Use distinct statuses ("draft-keep"/"draft-discard") so the journal and retrospective can distinguish drafts from iterations.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Baseline computation | Custom dummy models | `gsd_ml.baselines.tabular.compute_baselines()` | Handles stratified CV, multiple strategies |
| Baseline gating | Manual comparison | `gsd_ml.baselines.tabular.passes_baseline_gate()` | Handles direction, all-baselines check |
| Error analysis | Custom metrics | `gsd_ml.diagnostics.diagnose_*()` | Handles bias, correlations, confused pairs |
| Family selection | Hardcoded model lists | `gsd_ml.drafts.ALGORITHM_FAMILIES` | Centralized, domain-aware |
| Draft selection | Manual comparison | `gsd_ml.drafts.select_best_draft()` | Handles direction, None filtering |
| Stagnation detection | Counter logic | `gsd_ml.stagnation.check_stagnation()` | Uses SessionState.consecutive_reverts |
| Branch creation | Raw git commands | `gsd_ml.stagnation.trigger_stagnation_branch()` | Handles checkout, branch, counter reset |

## Common Pitfalls

### Pitfall 1: Baselines Not Persisted Across Context Resets
**What goes wrong:** Baselines computed in scaffold phase but not saved to disk. After context reset, the baseline gate can't check because baselines are gone.
**How to avoid:** Save baselines dict to `.ml/config.json` during scaffold. Read from config on each loop iteration. `SessionState.baselines` field exists for this.

### Pitfall 2: Diagnostics Require Predictions File
**What goes wrong:** train.py doesn't save predictions.csv, so diagnostics call fails.
**How to avoid:** The template already saves predictions.csv. Add a check in the workflow: if predictions.csv doesn't exist, skip diagnostics for this iteration.

### Pitfall 3: Multi-Draft Git Conflicts
**What goes wrong:** Draft commits overwrite each other's train.py. After selecting best draft, can't get back to it.
**How to avoid:** Each draft commits. After all drafts, `git checkout {best_draft_commit} -- train.py` to restore the best draft's train.py. Or simply checkout the best draft's commit hash.

### Pitfall 4: Stagnation Branch Loses State Files
**What goes wrong:** `trigger_stagnation_branch()` checks out best-ever commit, which may have older state files (results.jsonl, checkpoint.json).
**How to avoid:** Before branching, stash or save current state files. After creating the branch, restore state files. Or: only checkout train.py from the best commit, not the whole tree.

### Pitfall 5: All Families Exhausted
**What goes wrong:** Stagnation triggers but all families in `ALGORITHM_FAMILIES["tabular"]` have been tried. No new family to switch to.
**How to avoid:** Check `tried_families` against available families. If all tried, log it and continue iterating with current family (try hyperparameter variations instead).

### Pitfall 6: Baseline Gate Too Strict Early On
**What goes wrong:** First experiment is a simple model that doesn't beat baselines, gets reverted, never gets a chance to iterate.
**How to avoid:** The baseline gate should apply AFTER the multi-draft phase. During drafts, the gate is informational only. During iteration, the gate enforces.

## Code Examples

### Computing and Storing Baselines (INTEL-01)
```python
# In workflow Step 2.7 -- already exists, needs persistence added
import json, pandas as pd
from prepare import load_data, split_data, build_preprocessor
from gsd_ml.baselines.tabular import compute_baselines

df = load_data('{dataset_path}')
X_train, X_test, y_train, y_test = split_data(df, '{target_column}')
preprocessor = build_preprocessor(X_train)
X_proc = preprocessor.fit_transform(X_train)
baselines = compute_baselines(X_proc, y_train, '{scoring}', '{task}')

# Persist to config.json
config = json.loads(Path('.ml/config.json').read_text())
config['baselines'] = baselines
Path('.ml/config.json').write_text(json.dumps(config, indent=2))
print(json.dumps(baselines))
```

### Baseline Gate Check (INTEL-02)
```python
# After DeviationHandler returns "keep" in Step 3.4
from gsd_ml.baselines.tabular import passes_baseline_gate
config = json.loads(Path('.ml/config.json').read_text())
baselines = config.get('baselines', {})
if baselines and not passes_baseline_gate(metric_value, baselines, '{direction}'):
    # Beats previous best but not baselines -- revert
    decision = "revert"
    print("Reverted: metric does not beat baselines")
```

### Running Diagnostics (INTEL-03)
```python
# After train.py runs and produces predictions.csv
import json, pandas as pd
from gsd_ml.diagnostics import diagnose_regression, diagnose_classification

preds = pd.read_csv('.ml/predictions.csv')
if '{task}' == 'classification':
    diag = diagnose_classification(preds['y_true'].values, preds['y_pred'].values)
else:
    diag = diagnose_regression(preds['y_true'].values, preds['y_pred'].values)

Path('.ml/diagnostics.json').write_text(json.dumps(diag, indent=2, default=str))
print(json.dumps(diag, default=str))
```

### Multi-Draft Phase (INTEL-05)
```python
# Get available families for domain
from gsd_ml.drafts import get_families_for_domain, DraftResult, select_best_draft
families = get_families_for_domain('tabular')
# families = {"linear": {...}, "random_forest": {...}, "xgboost": {...}, ...}

# After running all drafts:
results = [
    DraftResult(name="linear", metric_value=0.72, status="draft-keep",
                commit_hash="abc1234", description="LogisticRegression baseline"),
    DraftResult(name="xgboost", metric_value=0.85, status="draft-keep",
                commit_hash="def5678", description="XGBClassifier defaults"),
    # ...
]
best = select_best_draft(results, direction='{direction}')
# Checkout best.commit_hash and continue iteration
```

### Stagnation Check (INTEL-06/07)
```python
# After a revert in Step 3.4
from gsd_ml.stagnation import check_stagnation, trigger_stagnation_branch
from gsd_ml.drafts import get_families_for_domain

state.consecutive_reverts += 1
if check_stagnation(state, threshold=3):
    families = get_families_for_domain('tabular')
    untried = [f for f in families if f not in state.tried_families]
    if untried:
        new_family = untried[0]
        branch = trigger_stagnation_branch('.', state, new_family)
        state.tried_families.append(new_family)
        # Edit train.py for new_family model class
```

## State of the Art

| Old Approach (mlforge) | Current Approach (gsd-ml) | Impact |
|------------------------|--------------------------|--------|
| Engine calls Python functions directly | Workflow markdown instructs Claude Code | All intelligence is workflow-level, not engine-level |
| Config dataclass for baselines | JSON config.json survives context resets | Must persist baselines to disk |
| GitPython for branching | subprocess.run (already ported) | Already handled in Phase 1 |
| Intelligence modules tightly coupled | Standalone pure functions | Easy to call from workflow bash snippets |

## Open Questions

1. **Multi-draft experiment count against budget?**
   - Drafts consume experiment budget slots (e.g., 5 drafts = 5 of 25 experiments used)
   - Recommendation: Yes, count drafts against budget. They are real experiments. But consider increasing default budget when drafts are enabled.

2. **Feature-error correlation in diagnostics**
   - `diagnose_regression()` accepts optional X and feature_names for correlation analysis
   - To use this, the workflow needs to load X_test from prepare.py after predictions -- slightly more complex
   - Recommendation: Start without feature correlations (just use y_true, y_pred). Add X-based correlations as a v2 enhancement.

3. **How many draft families to try?**
   - `ALGORITHM_FAMILIES["tabular"]` has 5 families (linear, random_forest, xgboost, lightgbm, svm)
   - Recommendation: Default to 3 families (linear, random_forest, xgboost) -- the most commonly useful. SVM is slow and rarely best for tabular. LightGBM overlaps heavily with XGBoost. Make configurable via `config.json`.

4. **Stagnation threshold value**
   - Default is 3 consecutive reverts
   - Recommendation: Keep 3 as default, store in config.json as `stagnation_threshold` for tunability.

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | `python/pyproject.toml` |
| Quick run command | `source .venv/bin/activate && python -m pytest python/tests/ -x -q` |
| Full suite command | `source .venv/bin/activate && python -m pytest python/tests/ -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| INTEL-01 | Baselines computed before experimentation | unit | `python -m pytest python/tests/test_baselines.py -x` | Yes (12 tests) |
| INTEL-02 | Baseline gate rejects models below baseline | unit | `python -m pytest python/tests/test_baselines.py::TestPassesBaselineGate -x` | Yes |
| INTEL-03 | Diagnostics analyze predictions | unit | `python -m pytest python/tests/test_diagnostics.py -x` | Yes (15 tests) |
| INTEL-04 | Diagnostics injected into next iteration | manual-only | Verify diagnostics.json read before train.py edit in workflow | N/A |
| INTEL-05 | Multi-draft explores diverse solutions | unit | `python -m pytest python/tests/test_drafts.py -x` | Yes (13 tests) |
| INTEL-06 | Stagnation detected after N reverts | unit | `python -m pytest python/tests/test_stagnation.py -x` | Yes (14 tests) |
| INTEL-07 | Branch-on-stagnation creates explore branch | unit | `python -m pytest python/tests/test_stagnation.py -x` | Yes |

### Sampling Rate
- **Per task commit:** `source .venv/bin/activate && python -m pytest python/tests/ -x -q`
- **Per wave merge:** `source .venv/bin/activate && python -m pytest python/tests/ -q`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
None -- existing test infrastructure covers all phase requirements. All 54 intelligence tests pass. The phase work is workflow integration (markdown), not new Python code.

## Sources

### Primary (HIGH confidence)
- Direct inspection of `gsd_ml` source code (diagnostics.py, drafts.py, stagnation.py, baselines/tabular.py)
- Direct inspection of `ml-run.md` workflow
- Direct inspection of `train-tabular.py` template
- Direct inspection of `state.py` SessionState fields
- Test execution: 54/54 tests passing in venv

### Secondary (MEDIUM confidence)
- mlforge predecessor architecture (lived experience, same author)

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All modules already ported, tested, and inspected
- Architecture: HIGH - Integration points clearly identified in existing workflow
- Pitfalls: HIGH - Based on direct code inspection and mlforge experience

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- no external dependencies changing)
