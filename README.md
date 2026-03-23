# gsd-ml

Claude Code native autonomous ML research tool.

[![npm version](https://img.shields.io/npm/v/gsd-ml.svg)](https://www.npmjs.com/package/gsd-ml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

gsd-ml turns Claude Code into an autonomous ML researcher. Instead of spawning subprocesses or double-billing API calls, Claude Code **is** the researcher -- it edits train.py, runs experiments via Bash, parses metrics, and makes keep/revert decisions directly using git. Ships as an npm package that installs skills and workflows into `~/.claude/`, plus a Python utilities package (`gsd_ml`) for data profiling, checkpointing, and diagnostics.

## Install

```bash
# 1. Install skills + workflows
npm install -g gsd-ml
gsd-ml                    # copies skills/workflows to ~/.claude/

# 2. Install Python utilities
pip install gsd-ml        # from PyPI
# or from repo:
pip install ./python
```

Optional extras for deep learning and fine-tuning:

```bash
pip install "gsd-ml[dl]"   # torch, timm, transformers
pip install "gsd-ml[ft]"   # torch, peft, trl, transformers
```

## Quick Start

In Claude Code, run:

```
/gsd:ml data.csv target_column
```

This profiles your dataset, scaffolds a `.ml/` experiment directory, runs iterative training with automatic keep/revert decisions, and exports the best model.

## Domains

| Domain | Command | Models |
|--------|---------|--------|
| Tabular | `/gsd:ml data.csv target` | sklearn, XGBoost, LightGBM |
| DL Image | `/gsd:ml images/ --domain dl --task image_classification` | timm (ResNet, EfficientNet, ...) |
| DL Text | `/gsd:ml data.csv target --domain dl --task text_classification` | transformers |
| Fine-Tuning | `/gsd:ml data.jsonl --domain ft --model-name meta-llama/...` | peft, trl (LoRA/QLoRA) |

## Skills

| Skill | Purpose |
|-------|---------|
| `/gsd:ml` | Run a full ML experiment |
| `/gsd:ml-status` | Show experiment history and metrics |
| `/gsd:ml-resume` | Resume an interrupted experiment |
| `/gsd:ml-clean` | Remove experiment artifacts (.ml/ directory) |
| `/gsd:ml-diagnose` | Run diagnostics on current model performance |

## How It Works

```
Skill (/gsd:ml) -> Workflow (ml-run.md) -> Claude Code executes with native tools
```

1. **Skills** (`~/.claude/commands/gsd-ml/`) are Claude Code slash commands with YAML frontmatter
2. **Workflows** (`~/.claude/gsd-ml/workflows/`) are step-by-step markdown instructions that Claude Code follows
3. Claude Code reads/writes files, runs training via Bash, parses metrics, and manages experiment state through git

Experiment state lives in `.ml/`:
- `config.json` -- experiment configuration (domain, target, metric, iterations)
- `checkpoint.json` -- current progress (iteration, best score, model path)
- `results.csv` -- metric history across iterations
- `journal.jsonl` -- detailed log of each iteration's changes and outcomes

## From mlforge

gsd-ml replaces [mlforge](https://github.com/robertlupo1997/mlforge)'s subprocess-spawning CLI with native Claude Code execution. Same experiment structure, same Python utilities, but Claude Code IS the researcher instead of being spawned as a subprocess.

**Migration:**
- Replace `from mlforge` imports with `from gsd_ml`
- Replace `mlforge` CLI commands with `/gsd:ml` slash commands
- Experiment directories (`.ml/`) use the same structure
- All Python utilities (profiler, checkpoint, guardrails, diagnostics, drafts, stagnation) carry over with identical APIs

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.11+
- Node.js 16.7+
