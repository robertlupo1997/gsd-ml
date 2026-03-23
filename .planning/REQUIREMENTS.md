# Requirements: gsd-ml

**Defined:** 2026-03-22
**Core Value:** Claude Code autonomously runs structured ML experiments without subprocess spawning or double-billing

## v1 Requirements

### Package & Distribution

- [x] **PKG-01**: npm package installs skills into ~/.claude/commands/gsd-ml/
- [x] **PKG-02**: npm package installs workflows, references, templates into ~/.claude/gsd-ml/
- [x] **PKG-03**: Python package (gsd_ml) installable via pip/uv with ML utilities
- [x] **PKG-04**: Installer validates Python package works after install

### Dataset Profiling

- [x] **PROF-01**: Auto-detect task type (classification vs regression) from target column
- [x] **PROF-02**: Auto-select appropriate metric based on task type
- [x] **PROF-03**: Detect data leakage and warn user
- [x] **PROF-04**: Report dataset statistics (rows, features, missing %, types)

### Experiment Scaffolding

- [x] **SCAF-01**: Create .ml/ state directory with config, checkpoint, journal files
- [x] **SCAF-02**: Generate domain-appropriate frozen prepare.py
- [x] **SCAF-03**: Generate domain-appropriate starter train.py
- [x] **SCAF-04**: Create git branch for experiment run (ml/run-{id})

### Experiment Loop

- [x] **LOOP-01**: Claude Code edits train.py directly (no subprocess spawning)
- [x] **LOOP-02**: Claude Code runs train.py via Bash and parses JSON metric from stdout
- [x] **LOOP-03**: Keep decision: git commit on improvement
- [x] **LOOP-04**: Revert decision: git checkout on non-improvement
- [x] **LOOP-05**: Retry decision: re-run with reduced resources on OOM
- [x] **LOOP-06**: Stop decision: halt on repeated OOM or guardrail trip

### Guardrails

- [x] **GUARD-01**: Enforce experiment count limit
- [x] **GUARD-02**: Enforce time budget (minutes)
- [x] **GUARD-03**: Enforce disk space minimum (1GB free)
- [x] **GUARD-04**: Stop gracefully when any guardrail trips

### Intelligence

- [x] **INTEL-01**: Compute baselines (naive strategies) before experimentation
- [x] **INTEL-02**: Baseline gate: model must beat baselines to be kept
- [x] **INTEL-03**: Diagnostics: analyze worst predictions, bias, feature-error correlations
- [x] **INTEL-04**: Inject diagnostics into next iteration prompt
- [x] **INTEL-05**: Multi-draft phase: 3-5 diverse initial solutions, pick best
- [x] **INTEL-06**: Stagnation detection: N consecutive reverts triggers model family switch
- [x] **INTEL-07**: Branch-on-stagnation: git branch from best-ever, try different family

### State & Recovery

- [x] **STATE-01**: Checkpoint saves after every experiment iteration
- [ ] **STATE-02**: Resume from checkpoint after context reset or crash
- [x] **STATE-03**: Append-only results.jsonl survives partial writes
- [x] **STATE-04**: Human-readable experiments.md journal updated per iteration

### Tabular Domain

- [x] **TAB-01**: sklearn, XGBoost, LightGBM model families supported
- [x] **TAB-02**: Metrics: accuracy, f1, f1_weighted, r2, rmse, mae
- [x] **TAB-03**: Cross-validation evaluation in train.py
- [x] **TAB-04**: Tabular-specific baselines (most_frequent, stratified, mean, median)

### Deep Learning Domain

- [ ] **DL-01**: PyTorch + timm for image classification
- [ ] **DL-02**: PyTorch + transformers for text classification
- [ ] **DL-03**: GPU-aware training templates
- [ ] **DL-04**: DL-specific baselines (random, most_frequent)

### Fine-Tuning Domain

- [ ] **FT-01**: LoRA/QLoRA via peft and trl
- [ ] **FT-02**: HuggingFace model loading and adapter training
- [ ] **FT-03**: Metrics: perplexity, rouge1, rougeL, loss
- [ ] **FT-04**: FT-specific baselines (random, base_model)

### Finalization

- [x] **FIN-01**: Export best model artifact with metadata.json sidecar
- [x] **FIN-02**: Generate retrospective markdown (what worked, what didn't, trajectory)
- [x] **FIN-03**: Tag best commit in git (ml-best-{run_id})

### Supporting Skills

- [ ] **SKILL-01**: /gsd:ml-status shows past experiment runs
- [ ] **SKILL-02**: /gsd:ml-resume loads checkpoint and re-enters experiment loop
- [ ] **SKILL-03**: /gsd:ml-clean removes .ml/ directories and experiment branches
- [ ] **SKILL-04**: /gsd:ml-diagnose runs diagnostics on current model standalone

## v2 Requirements

### Multi-Agent

- **MULTI-01**: Parallel experiment agents via Claude Code task-based parallelism
- **MULTI-02**: Shared scoreboard across parallel agents
- **MULTI-03**: Verification agent re-runs best solution

### Advanced

- **ADV-01**: Custom domain plugins (user-defined)
- **ADV-02**: Hyperparameter search strategies beyond random/grid
- **ADV-03**: Feature engineering suggestions from diagnostics
- **ADV-04**: Completion notifications (desktop/webhook)

## Out of Scope

| Feature | Reason |
|---------|--------|
| Web UI / dashboard | CLI/Claude Code only, keep it simple |
| Cloud job submission | Local-first, single machine |
| Swarm mode (v1) | Subprocess parallelism doesn't translate; redesign in v2 |
| Real-time data | Batch input only (CSV, Parquet, JSONL) |
| Training LLMs from scratch | Fine-tuning only |
| Replacing GSD | Domain-specific companion, not a fork |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| PKG-01 | Phase 1 | Complete |
| PKG-02 | Phase 1 | Complete |
| PKG-03 | Phase 1 | Complete |
| PKG-04 | Phase 1 | Complete |
| PROF-01 | Phase 2 | Complete |
| PROF-02 | Phase 2 | Complete |
| PROF-03 | Phase 2 | Complete |
| PROF-04 | Phase 2 | Complete |
| SCAF-01 | Phase 2 | Complete |
| SCAF-02 | Phase 2 | Complete |
| SCAF-03 | Phase 2 | Complete |
| SCAF-04 | Phase 2 | Complete |
| LOOP-01 | Phase 2 | Complete |
| LOOP-02 | Phase 2 | Complete |
| LOOP-03 | Phase 2 | Complete |
| LOOP-04 | Phase 2 | Complete |
| LOOP-05 | Phase 2 | Complete |
| LOOP-06 | Phase 2 | Complete |
| GUARD-01 | Phase 2 | Complete |
| GUARD-02 | Phase 2 | Complete |
| GUARD-03 | Phase 2 | Complete |
| GUARD-04 | Phase 2 | Complete |
| INTEL-01 | Phase 3 | Complete |
| INTEL-02 | Phase 3 | Complete |
| INTEL-03 | Phase 3 | Complete |
| INTEL-04 | Phase 3 | Complete |
| INTEL-05 | Phase 3 | Complete |
| INTEL-06 | Phase 3 | Complete |
| INTEL-07 | Phase 3 | Complete |
| STATE-01 | Phase 2 | Complete |
| STATE-02 | Phase 5 | Pending |
| STATE-03 | Phase 2 | Complete |
| STATE-04 | Phase 2 | Complete |
| TAB-01 | Phase 2 | Complete |
| TAB-02 | Phase 2 | Complete |
| TAB-03 | Phase 2 | Complete |
| TAB-04 | Phase 2 | Complete |
| DL-01 | Phase 4 | Pending |
| DL-02 | Phase 4 | Pending |
| DL-03 | Phase 4 | Pending |
| DL-04 | Phase 4 | Pending |
| FT-01 | Phase 4 | Pending |
| FT-02 | Phase 4 | Pending |
| FT-03 | Phase 4 | Pending |
| FT-04 | Phase 4 | Pending |
| FIN-01 | Phase 2 | Complete |
| FIN-02 | Phase 2 | Complete |
| FIN-03 | Phase 2 | Complete |
| SKILL-01 | Phase 5 | Pending |
| SKILL-02 | Phase 5 | Pending |
| SKILL-03 | Phase 5 | Pending |
| SKILL-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 48 total
- Mapped to phases: 48
- Unmapped: 0

---
*Requirements defined: 2026-03-22*
*Last updated: 2026-03-22 after initial definition*
