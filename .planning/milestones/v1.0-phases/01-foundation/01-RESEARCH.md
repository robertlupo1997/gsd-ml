# Phase 1: Foundation - Research

**Researched:** 2026-03-22
**Domain:** npm package distribution (GSD pattern), Python package porting (mlforge to gsd_ml)
**Confidence:** HIGH

## Summary

Phase 1 creates the gsd-ml distribution infrastructure: an npm package that installs Claude Code skills, workflows, references, and templates into `~/.claude/`, plus a pip-installable Python package (`gsd_ml`) containing all ported ML utilities from mlforge. This is a mechanical porting and packaging task with well-understood patterns.

The npm package follows the exact same pattern as `get-shit-done-cc` (v1.22.4): a `bin/install.js` entry point that copies directories to `~/.claude/`, with path replacement for runtime compatibility. The Python package is a straightforward restructuring of mlforge's 17 source files (~1986 lines total) with 3 specific adaptations: (1) change `mlforge.*` imports to `gsd_ml.*`, (2) replace GitPython usage with subprocess `git` calls, (3) replace `Config` dataclass with JSON config loading in guardrails.

**Primary recommendation:** Port Python files first (mechanical import changes), then build the npm package skeleton following the exact GSD install.js pattern. Templates (train.py.j2) must be de-Jinja2'd into static Python files with placeholder constants.

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|-----------------|
| PKG-01 | npm package installs skills into ~/.claude/commands/gsd-ml/ | GSD install.js pattern fully documented; copyWithPathReplacement handles .md files with path templating |
| PKG-02 | npm package installs workflows, references, templates into ~/.claude/gsd-ml/ | Mirrors GSD's `get-shit-done/` directory layout (workflows/, references/, templates/, bin/) |
| PKG-03 | Python package (gsd_ml) installable via pip/uv with ML utilities | pyproject.toml structure documented; 17 files to port with dependency list identified |
| PKG-04 | Installer validates Python package works after install | install.js can run `python -c "from gsd_ml..."` as post-install validation step |
</phase_requirements>

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Node.js | >=16.7.0 | npm package runtime for install.js | Same as GSD; uses only stdlib (fs, path, os) |
| Python | >=3.11 | gsd_ml package runtime | mlforge requires 3.11+ for tomllib, `X \| None` syntax |
| hatchling | latest | Python build backend | Same as mlforge; simple, no config needed |

### Python Dependencies (gsd_ml)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| scikit-learn | >=1.5 | Tabular baselines, cross-validation, preprocessing | Core dependency (tabular/baselines, tabular/prepare, profiler) |
| pandas | >=2.0 | Data loading, profiling | Core dependency (profiler, tabular/prepare) |
| numpy | >=2.0 | Array operations, diagnostics | Core dependency (diagnostics, baselines) |
| xgboost | >=2.0 | Tabular ML model family | Core dependency (tabular domain) |
| lightgbm | >=4.0 | Tabular ML model family | Core dependency (tabular domain) |
| pyarrow | >=15.0 | Parquet file support | Core dependency (data loading) |

### Dependencies REMOVED from mlforge
| Library | Reason |
|---------|--------|
| gitpython | Replaced by subprocess `git` calls (Claude Code runs git natively) |
| jinja2 | Templates are now static .py files, not .j2 |
| optuna | Used in train.py templates only (user-side), not in gsd_ml package |
| rich | CLI formatting not needed (Claude Code handles output) |
| psutil | Not used by ported modules |

### Optional Dependencies (installed by user, not by gsd_ml)
| Library | Purpose | When Needed |
|---------|---------|-------------|
| torch, torchvision, timm | DL domain | Phase 4 |
| transformers, peft, trl | FT domain | Phase 4 |

## Architecture Patterns

### npm Package Structure
```
gsd-ml/
  package.json              # name: "gsd-ml", bin: { "gsd-ml": "bin/install.js" }
  bin/
    install.js              # Copies files to ~/.claude/, validates Python
  commands/
    gsd-ml/
      ml.md                 # Main /gsd:ml skill (Phase 2 content, stub for now)
  gsd-ml/                   # Installed to ~/.claude/gsd-ml/
    workflows/
      ml-run.md             # Main experiment workflow (Phase 2)
    references/
      domains.md            # Domain reference (tabular/dl/ft)
    templates/
      train-tabular.py      # Static train.py starter (de-Jinja2'd)
      train-dl.py           # Static train.py for DL
      train-ft.py           # Static train.py for FT
    bin/
      ml-tools.cjs          # Equivalent of gsd-tools.cjs for ML ops (Phase 2+)
  python/                   # Python package source
    pyproject.toml
    src/
      gsd_ml/
        __init__.py
        profiler.py
        state.py
        checkpoint.py
        guardrails.py
        diagnostics.py
        drafts.py
        stagnation.py
        results.py
        journal.py
        retrospective.py
        export.py
        baselines/
          __init__.py
          tabular.py
          deeplearning.py
          finetuning.py
        prepare/
          __init__.py
          tabular.py
          deeplearning.py
          finetuning.py
```

### Pattern 1: GSD Install.js Pattern
**What:** The npm package's `bin/install.js` copies skill files and supporting directories to `~/.claude/`.
**When to use:** This is the only install mechanism.
**Key behaviors (from GSD source):**
1. `package.json` has `"bin": { "gsd-ml": "bin/install.js" }` -- makes it executable via `npx gsd-ml`
2. `install.js` copies `commands/gsd-ml/` to `~/.claude/commands/gsd-ml/` (skill files)
3. `install.js` copies `gsd-ml/` to `~/.claude/gsd-ml/` (workflows, references, templates, bin)
4. Path replacement: replaces `~/.claude/` references in .md files with actual install path
5. For gsd-ml, also validate Python package: run `python -c "from gsd_ml..."` and warn if not installed

```javascript
// Source: GSD install.js pattern
const src = path.join(__dirname, '..');
const configDir = path.join(os.homedir(), '.claude');

// Copy commands
const cmdSrc = path.join(src, 'commands', 'gsd-ml');
const cmdDest = path.join(configDir, 'commands', 'gsd-ml');
copyWithPathReplacement(cmdSrc, cmdDest, pathPrefix, 'claude', true);

// Copy gsd-ml skill directory (workflows, references, templates)
const skillSrc = path.join(src, 'gsd-ml');
const skillDest = path.join(configDir, 'gsd-ml');
copyWithPathReplacement(skillSrc, skillDest, pathPrefix, 'claude');
```

### Pattern 2: Skill File Format
**What:** Claude Code skill files are .md with YAML frontmatter.
**Required frontmatter fields:** `name`, `description`, `argument-hint`, `allowed-tools`
**Example (from GSD):**
```markdown
---
name: gsd:ml
description: Run an autonomous ML experiment
argument-hint: "<dataset> <target> [--domain tabular|dl|ft]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
---
<objective>
Run an autonomous ML experiment on the given dataset.
</objective>

<execution_context>
@~/.claude/gsd-ml/workflows/ml-run.md
</execution_context>

<context>
Dataset: $ARGUMENTS
</context>

<process>
Execute the ml-run workflow end-to-end.
</process>
```

### Pattern 3: Python Import Adaptation
**What:** Change `from mlforge.X import Y` to `from gsd_ml.X import Y` across all files.
**Scope:** Mechanical find-replace. Specific files:
- `profiler.py`: `from mlforge.tabular.prepare import validate_no_leakage` -> `from gsd_ml.prepare.tabular import validate_no_leakage`
- `checkpoint.py`: `from mlforge.state import SessionState` -> `from gsd_ml.state import SessionState`
- `guardrails.py`: `from mlforge.config import Config` -> REMOVE (use JSON config dict instead)
- `guardrails.py`: `from mlforge.state import SessionState` -> `from gsd_ml.state import SessionState`
- `stagnation.py`: `from mlforge.git_ops import GitManager` -> REMOVE (use subprocess git)
- `stagnation.py`: `from mlforge.state import SessionState` -> `from gsd_ml.state import SessionState`
- `journal.py`: `from git import GitCommandError, Repo` -> REMOVE (use subprocess git)
- `retrospective.py`: `from mlforge.config import Config` -> use dict or simple params
- `retrospective.py`: `from mlforge.results import ResultsTracker` -> `from gsd_ml.results import ResultsTracker`
- `retrospective.py`: `from mlforge.state import SessionState` -> `from gsd_ml.state import SessionState`
- `export.py`: `from mlforge.config import Config` -> use dict or simple params
- `export.py`: `from mlforge.state import SessionState` -> `from gsd_ml.state import SessionState`

### Pattern 4: GitPython Removal
**What:** Replace GitPython with subprocess calls.
**Files affected:**
1. `journal.py` (line 16, 135-142): `get_last_diff()` uses `Repo` and `repo.git.diff("HEAD~1")`
   - Replace with: `subprocess.run(["git", "diff", "HEAD~1"], capture_output=True, text=True, cwd=repo_path)`
2. `stagnation.py` (line 9, 46-50): `trigger_stagnation_branch()` uses `GitManager.repo.git.checkout()` and `repo.create_head()`
   - Replace with: `subprocess.run(["git", "checkout", commit], ...)` and `subprocess.run(["git", "checkout", "-b", branch_name], ...)`

### Pattern 5: Config Dataclass to JSON Dict
**What:** `guardrails.py` depends on `Config` dataclass for `budget_experiments`, `budget_usd`, `budget_minutes`.
**Adaptation:** Accept a plain dict (loaded from `.ml/config.json`) instead of the `Config` dataclass. This keeps guardrails.py free of mlforge's config.py dependency.
```python
# Before (mlforge)
def __init__(self, config: Config, experiment_dir: Path) -> None:
    self.config = config  # config.budget_experiments, config.budget_usd, etc.

# After (gsd_ml)
def __init__(self, config: dict, experiment_dir: Path) -> None:
    self.config = config  # config["budget_experiments"], config["budget_usd"], etc.
```
Same for `retrospective.py` and `export.py` which reference `Config`.

### Anti-Patterns to Avoid
- **Copying mlforge's config.py:** The Config dataclass with TOML loading is mlforge-specific. gsd_ml uses JSON config read by Claude Code directly.
- **Keeping GitPython dependency:** Claude Code runs git natively. Python utilities should use `subprocess.run(["git", ...])` when they need git at all.
- **Making templates dynamic:** Train templates should be static .py files with placeholder constants (CSV_PATH, TARGET_COLUMN, etc.) that Claude Code fills in via Edit tool, NOT Jinja2 rendering.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| npm install mechanism | Custom copy scripts | Follow GSD install.js pattern exactly | Battle-tested with path replacement, verification, multi-runtime support |
| Python package build | setup.py / setuptools | hatchling + pyproject.toml | Modern standard, same as mlforge, zero config |
| Skill file format | Custom YAML/XML format | GSD frontmatter pattern (YAML + XML blocks) | Claude Code recognizes this format natively |
| Cross-validation | Custom CV loops | sklearn cross_val_score | Edge cases (stratification, scoring) already handled |

## Common Pitfalls

### Pitfall 1: Circular Import Between gsd_ml Modules
**What goes wrong:** Moving modules into subpackages (baselines/, prepare/) can create circular imports if __init__.py re-exports eagerly.
**Why it happens:** profiler.py imports from prepare.tabular, which imports from sklearn. If __init__.py tries to import everything, load order breaks.
**How to avoid:** Keep `__init__.py` files minimal (empty or with `__version__` only). Use explicit imports: `from gsd_ml.prepare.tabular import load_data`.
**Warning signs:** ImportError at package load time.

### Pitfall 2: Template De-Jinja2 Losing Placeholders
**What goes wrong:** Converting `{{ csv_path }}` to a static value means Claude Code can't fill it in.
**Why it happens:** Jinja2 variables need to become Python constants that Claude Code will Edit.
**How to avoid:** Convert Jinja2 variables to clearly marked Python constants:
```python
# Configuration (filled by Claude Code)
CSV_PATH = "__DATASET_PATH__"
TARGET_COLUMN = "__TARGET__"
METRIC = "__METRIC__"
TASK = "__TASK__"
```
Claude Code uses Edit tool to replace these placeholders.

### Pitfall 3: npm Package Missing `files` Field
**What goes wrong:** `npm publish` excludes needed directories.
**Why it happens:** npm only includes files listed in `files` array in package.json.
**How to avoid:** Explicitly list all directories: `"files": ["bin", "commands", "gsd-ml"]`. Note: `python/` does NOT ship in npm; it's a separate pip install.

### Pitfall 4: Python Package Not Finding Submodule Files
**What goes wrong:** `from gsd_ml.baselines.tabular import compute_baselines` fails.
**Why it happens:** Missing `__init__.py` in subpackages, or hatchling not finding packages.
**How to avoid:** Add `__init__.py` to every directory. Use `[tool.hatch.build.targets.wheel] packages = ["src/gsd_ml"]`.

### Pitfall 5: guardrails.py Config Attribute Access
**What goes wrong:** `self.config.budget_experiments` fails because config is now a dict.
**Why it happens:** Changing from Config dataclass to dict changes attribute access to key access.
**How to avoid:** Systematically replace all `self.config.X` with `self.config["X"]` or `self.config.get("X", default)` in guardrails.py, retrospective.py, export.py.

### Pitfall 6: Journal/Stagnation Missing subprocess Import
**What goes wrong:** Functions that previously used GitPython now fail.
**Why it happens:** Forgot to add `import subprocess` when removing `from git import ...`.
**How to avoid:** After removing GitPython imports, add subprocess import and rewrite the git operations.

## Code Examples

### pyproject.toml for gsd_ml
```toml
# Based on mlforge's pyproject.toml, adapted for gsd_ml
[project]
name = "gsd-ml"
version = "0.1.0"
description = "Python ML utilities for gsd-ml (Claude Code ML research tool)"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [{name = "Robert Lupo"}]

dependencies = [
    "scikit-learn>=1.5",
    "pandas>=2.0",
    "numpy>=2.0",
    "xgboost>=2.0",
    "lightgbm>=4.0",
    "pyarrow>=15.0",
]

[project.optional-dependencies]
dl = [
    "torch>=2.4",
    "torchvision>=0.19",
    "timm>=1.0",
    "transformers>=4.45",
    "datasets>=3.0",
]
ft = [
    "peft>=0.14",
    "trl>=0.14",
    "bitsandbytes>=0.45",
    "evaluate>=0.4",
    "rouge-score>=0.1",
    "transformers>=4.45",
    "datasets>=3.0",
]

[dependency-groups]
dev = ["pytest", "ruff"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/gsd_ml"]

[tool.ruff]
target-version = "py311"
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "W", "I", "UP", "B"]
ignore = ["E501"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

### package.json for npm
```json
{
  "name": "gsd-ml",
  "version": "0.1.0",
  "description": "Claude Code native ML research tool - skills, workflows, and templates",
  "bin": {
    "gsd-ml": "bin/install.js"
  },
  "files": [
    "bin",
    "commands",
    "gsd-ml"
  ],
  "keywords": ["claude", "claude-code", "ml", "machine-learning", "automl"],
  "author": "Robert Lupo",
  "license": "MIT",
  "engines": {
    "node": ">=16.7.0"
  }
}
```

### journal.py get_last_diff Without GitPython
```python
# Source: adapted from mlforge/journal.py, removing GitPython
import subprocess

def get_last_diff(repo_path: Path | str) -> str | None:
    """Return the git diff between HEAD and HEAD~1."""
    result = subprocess.run(
        ["git", "diff", "HEAD~1"],
        capture_output=True, text=True,
        cwd=str(repo_path),
    )
    if result.returncode != 0:
        return None
    return result.stdout if result.stdout else None
```

### stagnation.py Without GitPython
```python
# Source: adapted from mlforge/intelligence/stagnation.py
import subprocess

def trigger_stagnation_branch(
    repo_path: Path | str,
    state: SessionState,
    new_family: str,
) -> str | None:
    """Create an exploration branch from the best-ever commit."""
    if state.best_commit is None:
        return None

    cwd = str(repo_path)
    subprocess.run(["git", "checkout", state.best_commit], cwd=cwd, check=True)

    branch_name = f"explore-{new_family}"
    subprocess.run(["git", "checkout", "-b", branch_name], cwd=cwd, check=True)

    state.consecutive_reverts = 0
    return branch_name
```

### guardrails.py With JSON Config
```python
# Source: adapted from mlforge/guardrails.py
class ResourceGuardrails:
    def __init__(self, config: dict, experiment_dir: Path) -> None:
        self.config = config
        self.experiment_dir = experiment_dir
        self._start_time = time.time()
        self.min_free_disk_gb = config.get("min_free_disk_gb", 1.0)

    def stop_reason(self, state: SessionState) -> str | None:
        if state.experiment_count >= self.config.get("budget_experiments", 50):
            return f"Experiment count limit reached: {state.experiment_count}/{self.config['budget_experiments']}"
        if state.cost_spent_usd >= self.config.get("budget_usd", 5.0):
            return f"Cost cap reached: ${state.cost_spent_usd:.2f}/${self.config['budget_usd']:.2f}"
        elapsed = time.time() - self._start_time
        budget_seconds = self.config.get("budget_minutes", 60) * 60
        if elapsed >= budget_seconds:
            return f"Time budget exceeded: {elapsed / 60:.1f}min/{self.config['budget_minutes']}min"
        usage = shutil.disk_usage(self.experiment_dir)
        free_gb = usage.free / (1024**3)
        if free_gb < self.min_free_disk_gb:
            return f"Disk space low: {free_gb:.2f}GB free (min {self.min_free_disk_gb}GB)"
        return None
```

## State of the Art

| Old Approach (mlforge) | New Approach (gsd_ml) | Impact |
|------------------------|----------------------|--------|
| GitPython for git ops | subprocess.run(["git", ...]) | Removes dependency, Claude Code does most git ops itself |
| Config dataclass + TOML | Plain dict from JSON | Simpler, Claude Code reads/writes JSON naturally |
| Jinja2 templates | Static .py with placeholder constants | Claude Code uses Edit tool to fill values |
| CLI entry point (mlforge.cli) | Skill file (/gsd:ml) | No Python CLI needed; Claude Code is the interface |

**Dropped from mlforge (not ported):**
- `engine.py` -- Claude Code IS the engine; it runs the experiment loop directly
- `cli.py` -- No CLI; Claude Code skills replace this
- `swarm/` -- Subprocess parallelism; v2 will use Claude Code Task tool
- `hooks.py` -- Subprocess hooks not applicable
- `progress.py` -- Claude Code handles progress display
- `plugins.py` -- Domain plugins replaced by workflow + template pattern
- `config.py` -- Config dataclass replaced by JSON dict
- `git_ops.py` -- GitManager class replaced by subprocess git + Claude Code native git
- `scaffold.py` -- Claude Code scaffolds via Write tool + templates
- `gpu.py` -- Inlined where needed (DL/FT prepare files already have device detection)
- `notify.py` -- Not applicable in Claude Code context
- `status.py` -- Replaced by /gsd:ml-status skill
- `clean.py` -- Replaced by /gsd:ml-clean skill
- `logging_config.py` -- Not needed; Claude Code manages output

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest (latest) |
| Config file | python/pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `cd python && python -m pytest tests/ -x -q` |
| Full suite command | `cd python && python -m pytest tests/ -v` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PKG-01 | npm installs skills to ~/.claude/commands/gsd-ml/ | integration | `node bin/install.js --claude && test -d ~/.claude/commands/gsd-ml/` | -- Wave 0 |
| PKG-02 | npm installs workflows/refs/templates to ~/.claude/gsd-ml/ | integration | `node bin/install.js --claude && test -d ~/.claude/gsd-ml/workflows/` | -- Wave 0 |
| PKG-03 | Python package importable with all utilities | unit | `cd python && python -m pytest tests/test_imports.py -x` | -- Wave 0 |
| PKG-04 | Installer validates Python works | integration | Manual verification (install.js runs python check) | manual-only |

### Additional Python Unit Tests
| Module | Test File | Key Tests |
|--------|-----------|-----------|
| profiler.py | tests/test_profiler.py | task detection, metric selection, leakage detection |
| state.py | tests/test_state.py | SessionState creation, field defaults |
| checkpoint.py | tests/test_checkpoint.py | save/load roundtrip, atomic write |
| guardrails.py | tests/test_guardrails.py | budget checks with dict config, disk space, deviation handler |
| diagnostics.py | tests/test_diagnostics.py | regression/classification diagnostics |
| results.py | tests/test_results.py | JSONL append/load, best result, summary |
| journal.py | tests/test_journal.py | entry append, load, markdown render, get_last_diff |
| stagnation.py | tests/test_stagnation.py | check_stagnation threshold |
| drafts.py | tests/test_drafts.py | algorithm families structure |
| retrospective.py | tests/test_retrospective.py | markdown generation |
| export.py | tests/test_export.py | artifact copy, metadata.json |
| baselines/*.py | tests/test_baselines.py | tabular, DL, FT baseline computation |

### Sampling Rate
- **Per task commit:** `cd python && python -m pytest tests/ -x -q`
- **Per wave merge:** `cd python && python -m pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd:verify-work`

### Wave 0 Gaps
- [ ] `python/tests/test_imports.py` -- verifies all modules importable
- [ ] `python/tests/test_profiler.py` -- port from mlforge tests
- [ ] `python/tests/test_state.py` -- port from mlforge tests
- [ ] `python/tests/test_checkpoint.py` -- port from mlforge tests
- [ ] `python/tests/test_guardrails.py` -- adapt for JSON config
- [ ] `python/tests/test_diagnostics.py` -- port from mlforge tests
- [ ] `python/tests/test_results.py` -- port from mlforge tests
- [ ] `python/tests/test_journal.py` -- adapt for subprocess git
- [ ] `python/tests/test_baselines.py` -- port from mlforge tests
- [ ] `python/tests/test_retrospective.py` -- adapt for dict config
- [ ] `python/tests/test_export.py` -- adapt for dict config
- [ ] `python/tests/conftest.py` -- shared fixtures (tmp dirs, sample data)
- [ ] Framework install: `pip install -e "python/[dev]"` (or `uv pip install`)

## Open Questions

1. **Python package location within the repo**
   - What we know: npm package is root level (package.json at repo root). Python package needs its own directory.
   - Recommendation: Use `python/` subdirectory with its own `pyproject.toml`, `src/gsd_ml/`, and `tests/`. This keeps npm and Python concerns cleanly separated.

2. **Whether install.js should auto-install Python package**
   - What we know: GSD's install.js doesn't install Python packages.
   - Recommendation: install.js should CHECK if gsd_ml is importable and WARN if not, but not auto-install (user may want pip vs uv vs conda). Print install instructions: `pip install gsd-ml` (from PyPI) or `pip install -e python/` (from source).

3. **Template content for Phase 1**
   - What we know: Templates are needed for Phase 2 (core workflow). Phase 1 just needs the infrastructure.
   - Recommendation: Create stub template files with the structure and placeholder constants. Full content can be filled in Phase 2. The de-Jinja2 conversion of `tabular_train.py.j2` should happen now since it's a porting task.

## Sources

### Primary (HIGH confidence)
- GSD install.js source: `/home/tlupo/.npm/_npx/4db0de1f85c3165e/node_modules/get-shit-done-cc/bin/install.js` -- full install pattern, copyWithPathReplacement, verification
- GSD package.json: `/home/tlupo/.npm/_npx/4db0de1f85c3165e/node_modules/get-shit-done-cc/package.json` -- bin entry, files array, engines
- GSD skill files: `~/.claude/commands/gsd/*.md` -- frontmatter format (name, description, argument-hint, allowed-tools)
- mlforge source: `/home/tlupo/AutoML/src/mlforge/` -- all 17 files to port, imports, dependencies
- mlforge pyproject.toml: `/home/tlupo/AutoML/pyproject.toml` -- dependency list, build config
- mlforge tests: `/home/tlupo/AutoML/tests/mlforge/` -- existing test patterns to adapt

### Secondary (MEDIUM confidence)
- GSD directory layout: `~/.claude/get-shit-done/{workflows,references,templates,bin}/` -- verified by listing installed files

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - directly inspected GSD source and mlforge source
- Architecture: HIGH - GSD install pattern is production-proven (v1.22.4), mlforge porting is mechanical
- Pitfalls: HIGH - identified from actual source code analysis (import chains, config access patterns)

**File sizes (total to port):** 1986 lines of Python across 17 files
**Adaptation complexity:** LOW - 3 files need non-trivial changes (guardrails, journal, stagnation), rest are import-only changes

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable domain, no external API changes expected)
