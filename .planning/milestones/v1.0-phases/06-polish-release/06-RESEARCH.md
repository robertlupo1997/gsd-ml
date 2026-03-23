# Phase 6: Polish + Release - Research

**Researched:** 2026-03-22
**Domain:** npm publishing, error handling, documentation, test validation
**Confidence:** HIGH

## Summary

Phase 6 is a quality/release phase -- all 48 v1 feature requirements are already complete (checked off in REQUIREMENTS.md) with 188 Python tests passing. The work is: (1) add defensive error handling to the 5 workflow files, (2) write README.md, (3) verify package.json and npm publish readiness, (4) validate workflow-to-Python bridge call correctness.

The codebase is in good shape. The `npm publish --dry-run` already succeeds with 17 files / 92.3 kB unpacked. The package.json has all required fields. The main gaps are: no README.md, no `homepage`/`bugs` fields in package.json, no `.npmignore` (relying on `files` array which is fine), and workflow files lack pre-flight checks for missing Python deps.

**Primary recommendation:** Keep this to 2 plans max. Plan 1: error handling + workflow validation + package.json polish. Plan 2: README.md + npm publish verification.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- Error handling scope: Focus on workflow files (ml-run.md, ml-resume.md, ml-status.md, ml-clean.md, ml-diagnose.md) -- add defensive checks for: missing Python deps, corrupt/missing .ml/ state files, git branch conflicts, missing dataset files
- Python utilities already have reasonable error handling from mlforge port (188 tests passing)
- Workflow error messages should be actionable: tell user what went wrong AND how to fix it
- Don't add try/catch to every Python bridge call -- only where failure is likely (missing deps, corrupt state)
- Single README.md at repo root with sections: What it is, Install (npm + pip), Quick Start (tabular example), Domains (tabular/DL/FT), Skills reference table, How it works (brief architecture), Requirements (Python 3.10+, Claude Code)
- Keep README concise -- power-user tool for Claude Code users, not a beginner tutorial
- Include a "From mlforge" section for existing mlforge users
- Verify package.json metadata (name, version, description, repository, license, keywords)
- Verify `files` array includes all necessary dirs (bin, commands, gsd-ml)
- Verify install.js works from a clean npm install
- Python package (gsd_ml) is a separate pip install -- document in README, don't bundle in npm
- Version: publish as 0.1.0
- Verify all Python bridge calls in ml-run.md match actual gsd_ml API signatures
- Verify all file paths in workflow references resolve correctly after npm install
- Verify template __PLACEHOLDER__ constants are all documented for scaffold phase
- Follow GSD's own package structure for npm publish patterns
- Error handling should not be over-engineered -- the primary user is Claude Code itself following workflow instructions, not humans typing commands

### Claude's Discretion
- Exact error message wording
- README formatting and section ordering
- Whether to add a CHANGELOG.md
- Badge selection for README (npm version, license, etc.)

### Deferred Ideas (OUT OF SCOPE)
- AutoML integration (auto-sklearn, FLAML) -- potential v2 feature
- Multi-agent parallel experiments -- v2 MULTI-01 through MULTI-03
- Custom domain plugins -- v2 ADV-01
- Desktop/webhook notifications -- v2 ADV-04
</user_constraints>

## Standard Stack

This phase involves no new library dependencies. It is purely quality work on existing files.

### Core Tools
| Tool | Purpose | Why |
|------|---------|-----|
| npm | Package publishing | Standard npm registry publish |
| pytest | Test validation | Already configured in pyproject.toml, 188 tests passing |

### No New Dependencies
This phase adds zero new packages. All work is on existing workflow markdown files, package.json metadata, and README.md.

## Architecture Patterns

### Current Package Structure (verified)
```
gsd-ml/
  bin/install.js          # Entry point -- copies to ~/.claude/
  commands/gsd-ml/        # Skill files (5 skills)
    ml.md
    ml-clean.md
    ml-diagnose.md
    ml-resume.md
    ml-status.md
  gsd-ml/                 # Workflow/reference/template content
    workflows/            # 5 workflow .md files
    templates/            # 4 train template .py files
    references/           # metric-map.md
  package.json            # npm metadata
  python/                 # Separate pip package (NOT in npm)
    pyproject.toml
    src/gsd_ml/           # 14 Python modules
    tests/                # 15 test files, 188 tests
```

### npm Publish Readiness (current state)
- `npm pack --dry-run` succeeds: 17 files, 92.3 kB unpacked, 26.1 kB packed
- `files` array correctly limits to `["bin", "commands", "gsd-ml"]` -- excludes python/, .planning/, .venv/
- No `.npmignore` needed (the `files` whitelist approach is preferred)
- Missing: `homepage` and `bugs` fields (npm recommends these)
- Missing: `scripts.postinstall` is NOT used -- follows GSD pattern where user runs `gsd-ml` command manually after global install

### Pattern: Python Bridge Error Handling in Workflows

The workflows contain ~37 Python bridge calls (`python -c "from gsd_ml..."` or `python3 -c "from gsd_ml..."`). Error handling should be added at the **workflow instruction level** (telling Claude Code what to check), not by wrapping every call in try/catch.

**Recommended pattern for pre-flight check (add once at workflow start):**
```markdown
### Step 0: Pre-flight Checks

Verify Python package is available:
```bash
python3 -c "import gsd_ml" 2>&1
```

If this fails, STOP and print:
```
ERROR: gsd_ml Python package not found.
Install with: pip install ./python (from gsd-ml repo) or pip install gsd-ml
```
```

**Recommended pattern for corrupt state:**
```markdown
If the checkpoint load returns None or the JSON is malformed, print:
```
ERROR: Corrupt checkpoint at .ml/checkpoint.json
Fix: Delete .ml/checkpoint.json and run /gsd:ml to start fresh, or check the file manually.
```
```

### Pattern: Workflow-Level Validation Points

Error handling belongs at these specific points in each workflow:

| Workflow | Check Point | What to Verify |
|----------|-------------|----------------|
| ml-run.md | Start | Python deps available (gsd_ml importable) |
| ml-run.md | Step 1.2 | Dataset file/directory exists |
| ml-run.md | Step 2 (scaffold) | Git branch can be created (no conflicts) |
| ml-run.md | Step 3 (loop) | train.py outputs valid JSON metric |
| ml-resume.md | Start | Python deps + .ml/ directory + checkpoint.json exist |
| ml-resume.md | Step 2 | Checkpoint loads without corruption |
| ml-resume.md | Step 2 | Git branch from checkpoint still exists |
| ml-status.md | Start | Python deps available |
| ml-clean.md | Start | .ml/ directory exists |
| ml-diagnose.md | Start | Python deps + .ml/ + checkpoint exist |

### Anti-Patterns to Avoid
- **Over-wrapping Python calls:** Don't add try/except to every `python -c` call. Claude Code already sees stderr output. Only add explicit error handling where failure is **likely and confusing**.
- **Duplicating error handling in Python and workflow:** The Python modules already handle edge cases. Workflow error handling is for **missing prerequisites** (deps not installed, state files missing).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| npm publish validation | Custom publish script | `npm publish --dry-run` + `npm pack` | npm's built-in tools catch all packaging issues |
| README badges | Manual markdown | shields.io URLs | Standard, auto-updating |
| Python API signature checking | AST parsing tool | Manual grep comparison | Only ~37 calls to verify, faster to eyeball |

## Common Pitfalls

### Pitfall 1: python vs python3 Inconsistency
**What goes wrong:** Some workflow files use `python -c` and others use `python3 -c`. On many Linux systems, `python` is not available (only `python3`).
**Current state:** The workflows mostly use `python -c` in ml-run.md but `python3 -c` in ml-resume.md.
**How to avoid:** Standardize ALL workflow Python calls to `python3 -c`. This is the safest cross-platform choice.
**Warning signs:** `command not found: python` on fresh Ubuntu installs.

### Pitfall 2: Missing README in npm Package
**What goes wrong:** npm shows README content on the package page. Without README.md in the `files` array or at root, the npm page is blank.
**How to avoid:** Add `"README.md"` to the `files` array in package.json, or put it at package root (npm includes root README automatically even without listing it in `files`).
**Note:** npm automatically includes README.md from package root regardless of the `files` field. No change needed to `files` array.

### Pitfall 3: npm Publish Without .gitignore Causing Bloat
**What goes wrong:** Without proper exclusion, `.venv/`, `__pycache__/`, `.planning/` could end up in the tarball.
**Current state:** The `files` whitelist in package.json (`["bin", "commands", "gsd-ml"]`) already prevents this. Verified with `npm pack --dry-run` showing only 17 files. No issue here.

### Pitfall 4: install.js Fails on Windows Paths
**What goes wrong:** The `pathPrefix` uses forward slashes, but Windows uses backslashes.
**Current state:** install.js already handles this with `.replace(/\\/g, '/')`. No issue here.

### Pitfall 5: Stale Python Bridge Calls After Refactoring
**What goes wrong:** Workflow .md files reference Python function signatures that were changed during earlier phases.
**How to avoid:** For each `from gsd_ml.X import Y` in workflows, verify Y exists in the current Python source with the expected call signature.
**Context:** Phase 2 Plan 3 already fixed 6 mismatches. Need to verify no regressions from Phase 3-5 work.

## Code Examples

### README Structure (recommended)
```markdown
# gsd-ml

Claude Code native autonomous ML research tool.

[![npm version](https://img.shields.io/npm/v/gsd-ml.svg)](https://www.npmjs.com/package/gsd-ml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

[2-3 sentences explaining Claude Code runs ML experiments autonomously]

## Install

```bash
npm install -g gsd-ml
gsd-ml  # copies skills/workflows to ~/.claude/

pip install gsd-ml  # or: pip install ./python from repo
```

## Quick Start

```
/gsd:ml data.csv target_column
```

## Domains

| Domain | Command | Models |
|--------|---------|--------|
| Tabular | `/gsd:ml data.csv target` | sklearn, XGBoost, LightGBM |
| Deep Learning (Image) | `/gsd:ml images/ --domain dl --task image_classification` | timm (ResNet, EfficientNet, ...) |
| Deep Learning (Text) | `/gsd:ml data.csv target --domain dl --task text_classification` | transformers |
| Fine-Tuning | `/gsd:ml data.jsonl --domain ft --model-name meta-llama/...` | peft, trl (LoRA/QLoRA) |

## Skills

| Skill | Purpose |
|-------|---------|
| `/gsd:ml` | Run a full ML experiment |
| `/gsd:ml-status` | Show past experiment runs |
| `/gsd:ml-resume` | Resume interrupted experiment |
| `/gsd:ml-clean` | Remove experiment artifacts |
| `/gsd:ml-diagnose` | Run diagnostics on current model |

## How It Works

[Brief architecture description]

## From mlforge

[Migration notes for existing mlforge users]

## Requirements

- Claude Code
- Python 3.11+
- Node.js 16.7+
```

### package.json Additions (recommended)
```json
{
  "homepage": "https://github.com/robertlupo1997/gsd-ml#readme",
  "bugs": {
    "url": "https://github.com/robertlupo1997/gsd-ml/issues"
  }
}
```

### Pre-flight Check Pattern (for workflow files)
```markdown
### Pre-flight: Verify Dependencies

```bash
python3 -c "import gsd_ml; print('OK')" 2>&1
```

If this prints an error (ModuleNotFoundError), STOP and tell the user:
> gsd_ml Python package is not installed. Install with:
> `pip install gsd-ml` (from PyPI) or `pip install ./python` (from repo)

```bash
git status --porcelain 2>&1
```

If git is not available or the directory is not a git repo, STOP and tell the user:
> This directory must be a git repository. Run `git init` first.
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| `python -c` (no python3) | `python3 -c` everywhere | Python 3.12+ deprecation | Systems without `python` symlink fail |
| npm postinstall | bin command (manual run) | GSD pattern | Avoids npm security warnings about postinstall scripts |

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 9.0.2 |
| Config file | python/pyproject.toml `[tool.pytest.ini_options]` |
| Quick run command | `cd python && python3 -m pytest -x -q` |
| Full suite command | `cd python && python3 -m pytest -q` (requires venv with gsd_ml installed) |

### Important Note on Test Environment
Tests require the venv at `.venv/` to be activated (`source .venv/bin/activate`) because `gsd_ml` must be installed in the Python environment. Running `python3 -m pytest` without the venv results in 11 collection errors (ModuleNotFoundError for gsd_ml).

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| (quality) | All 188 Python tests pass | unit | `source .venv/bin/activate && cd python && python -m pytest -q` | Yes (15 files) |
| (quality) | npm pack includes correct files | smoke | `npm pack --dry-run` | manual |
| (quality) | install.js runs without error | smoke | `node bin/install.js` | manual |
| (quality) | Python bridge calls match API | integration | manual grep verification | manual |
| (quality) | README.md exists and renders | manual | `test -f README.md` | Wave 0 |

### Sampling Rate
- **Per task commit:** `source .venv/bin/activate && cd python && python -m pytest -x -q`
- **Per wave merge:** Full test suite + `npm pack --dry-run`
- **Phase gate:** Full suite green + successful `npm publish --dry-run`

### Wave 0 Gaps
None -- existing test infrastructure covers Python validation. README.md and workflow error handling are new file creation / file editing, not test-gated.

## Open Questions

1. **npm registry account**
   - What we know: Package name `gsd-ml` appears available on npm (no `npm show gsd-ml` result for an existing package)
   - What's unclear: Whether the user has an npm account with publish rights
   - Recommendation: Verify `npm whoami` works before attempting publish. If not logged in, `npm login` first.

2. **pyproject.toml says Python >=3.11 but CONTEXT.md says 3.10+**
   - What we know: pyproject.toml has `requires-python = ">=3.11"`, CONTEXT.md README spec says "Python 3.10+"
   - What's unclear: Which is the actual minimum
   - Recommendation: Use 3.11+ in README to match pyproject.toml (numpy>=2.0 requires 3.11+)

## Sources

### Primary (HIGH confidence)
- Direct codebase inspection: package.json, install.js, pyproject.toml, all workflow files
- `npm pack --dry-run` and `npm publish --dry-run` output
- `python3 -m pytest` output (188 passing in venv, 39 collected without venv)
- GSD package structure at `~/.claude/get-shit-done/`

### Secondary (MEDIUM confidence)
- `npm show get-shit-done-cc` for GSD publish pattern reference

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - no new deps, just polishing existing files
- Architecture: HIGH - package structure verified with npm pack, tests verified
- Pitfalls: HIGH - verified python/python3 inconsistency and bridge call counts directly

**Research date:** 2026-03-22
**Valid until:** 2026-04-22 (stable -- no moving targets in this phase)
