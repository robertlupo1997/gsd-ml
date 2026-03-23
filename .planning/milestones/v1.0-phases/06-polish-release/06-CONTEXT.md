# Phase 6: Polish + Release - Context

**Gathered:** 2026-03-23
**Status:** Ready for planning

<domain>
## Phase Boundary

Production-ready npm package published to registry. This phase covers error handling hardening, README documentation, workflow validation, and npm publish. All 48 v1 feature requirements are already complete — this phase is purely quality and release.

</domain>

<decisions>
## Implementation Decisions

### Error handling scope
- Focus on the workflow files (ml-run.md, ml-resume.md, ml-status.md, ml-clean.md, ml-diagnose.md) — add defensive checks for: missing Python deps, corrupt/missing .ml/ state files, git branch conflicts, missing dataset files
- Python utilities already have reasonable error handling from mlforge port (188 tests passing)
- Workflow error messages should be actionable: tell user what went wrong AND how to fix it
- Don't add try/catch to every Python bridge call — only where failure is likely (missing deps, corrupt state)

### README documentation
- Single README.md at repo root
- Sections: What it is, Install (npm + pip), Quick Start (tabular example), Domains (tabular/DL/FT), Skills reference table, How it works (brief architecture), Requirements (Python 3.10+, Claude Code)
- Keep it concise — this is a power-user tool for Claude Code users, not a beginner tutorial
- Include a "From mlforge" section for existing mlforge users explaining the migration

### npm publish readiness
- Verify package.json metadata (name, version, description, repository, license, keywords)
- Verify `files` array includes all necessary dirs (bin, commands, gsd-ml)
- Verify install.js works from a clean npm install (copies to ~/.claude/ correctly)
- Python package (gsd_ml) is a separate pip install — document in README, don't bundle in npm
- Version: publish as 0.1.0 (first public release, not yet battle-tested)

### Workflow validation
- Verify all Python bridge calls in ml-run.md match actual gsd_ml API signatures (Phase 2 Plan 3 already fixed 6 mismatches — verify no regressions)
- Verify all file paths in workflow references resolve correctly after npm install
- Verify template __PLACEHOLDER__ constants are all documented for scaffold phase

### Claude's Discretion
- Exact error message wording
- README formatting and section ordering
- Whether to add a CHANGELOG.md
- Badge selection for README (npm version, license, etc.)

</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- 188 existing Python tests across 13 test files — solid foundation, may need integration-level tests for workflow bridge calls
- `install.js`: copies commands/gsd-ml/ and gsd-ml/ directories to ~/.claude/ — already functional
- `package.json`: basic metadata present, needs review for publish readiness
- `python/pyproject.toml`: Python package config exists

### Established Patterns
- Skill files: YAML frontmatter + XML body in `commands/gsd-ml/`
- Workflows: markdown instruction files in `gsd-ml/workflows/`
- Python bridge: `python -c "from gsd_ml.X import Y; ..."` from Bash in workflows
- Templates: static .py files with `__PLACEHOLDER__` constants in `gsd-ml/templates/`
- References: markdown lookup tables in `gsd-ml/references/`

### Integration Points
- `bin/install.js` is the npm postinstall entry point
- Skills install to `~/.claude/commands/gsd-ml/`
- Workflows/templates/references install to `~/.claude/gsd-ml/`
- Python package installed separately via `pip install ./python` or `uv pip install ./python`

</code_context>

<specifics>
## Specific Ideas

- Follow GSD's own package structure for npm publish patterns (get-shit-done-cc as reference)
- Error handling should not be over-engineered — the primary user is Claude Code itself following workflow instructions, not humans typing commands

</specifics>

<deferred>
## Deferred Ideas

- AutoML integration (auto-sklearn, FLAML) — potential v2 feature
- Multi-agent parallel experiments — v2 MULTI-01 through MULTI-03
- Custom domain plugins — v2 ADV-01
- Desktop/webhook notifications — v2 ADV-04

</deferred>

---

*Phase: 06-polish-release*
*Context gathered: 2026-03-23*
