# gsd-ml

Claude Code native autonomous ML research tool.

[![npm version](https://img.shields.io/npm/v/gsd-ml.svg)](https://www.npmjs.com/package/gsd-ml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## What is this?

gsd-ml turns Claude Code into an autonomous ML researcher. Claude Code edits train.py, runs experiments via Bash, parses metrics, and makes keep/revert decisions through git — no subprocesses, no double-billing. Ships as an npm package (skills and workflows into `~/.claude/`) plus a Python utilities package (`gsd_ml`) for data profiling, checkpointing, and diagnostics.

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

For other domains:

```
/gsd:ml images/ --domain dl --task image_classification
/gsd:ml data.csv target --domain dl --task text_classification
/gsd:ml data.jsonl --domain ft --model-name meta-llama/Llama-3-8B
```

## Domains

| Domain | Command | Models |
|--------|---------|--------|
| Tabular | `/gsd:ml data.csv target` | sklearn, XGBoost, LightGBM |
| DL Image | `/gsd:ml images/ --domain dl --task image_classification` | timm (ResNet, EfficientNet, ...) |
| DL Text | `/gsd:ml data.csv target --domain dl --task text_classification` | transformers |
| Fine-Tuning | `/gsd:ml data.jsonl --domain ft --model-name meta-llama/...` | peft, trl (LoRA/QLoRA) |

> DL and FT domains check for GPU availability at startup. CPU-only machines still work but run slowly.

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
3. **Templates** (`~/.claude/gsd-ml/templates/`) provide starter train.py files for each domain (tabular, DL image, DL text, fine-tuning)
4. **References** (`~/.claude/gsd-ml/references/`) are lookup tables (e.g., metric-map.md maps metrics to sklearn scoring strings)
5. Claude Code reads/writes files, runs training via Bash, parses metrics, and manages experiment state through git

Experiment state lives in `.ml/`:
- `config.json` -- experiment configuration (domain, target, metric, guardrails)
- `checkpoint.json` -- current progress (iteration, best score, keeps/reverts)
- `results.jsonl` -- metric history across iterations
- `experiments.md` -- human-readable journal of each iteration

## From mlforge

gsd-ml replaces [mlforge](https://github.com/robertlupo1997/mlforge)'s subprocess-spawning CLI with native Claude Code execution.

**Migration:**
- Replace `from mlforge` with `from gsd_ml`
- Replace `mlforge` CLI commands with `/gsd:ml` slash commands
- `.ml/` directory structure is unchanged
- All Python utilities carry over with identical APIs

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code)
- Python 3.11+
- Node.js 16.7+
