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

- [ ] **PROF-01**: Auto-detect task type (classification vs regression) from target column
- [ ] **PROF-02**: Auto-select appropriate metric based on task type
- [ ] **PROF-03**: Detect data leakage and warn user
- [ ] **PROF-04**: Report dataset statistics (rows, features, missing %, types)

### Experiment Scaffolding

- [ ] **SCAF-01**: Create .ml/ state directory with config, checkpoint, journal files
- [ ] **SCAF-02**: Generate domain-appropriate frozen prepare.py
- [ ] **SCAF-03**: Generate domain-appropriate starter train.py
- [ ] **SCAF-04**: Create git branch for experiment run (ml/run-{id})

### Experiment Loop

- [ ] **LOOP-01**: Claude Code edits train.py directly (no subprocess spawning)
- [ ] **LOOP-02**: Claude Code runs train.py via Bash and parses JSON metric from stdout
- [ ] **LOOP-03**: Keep decision: git commit on improvement
- [ ] **LOOP-04**: Revert decision: git checkout on non-improvement
- [ ] **LOOP-05**: Retry decision: re-run with reduced resources on OOM
- [ ] **LOOP-06**: Stop decision: halt on repeated OOM or guardrail trip

### Guardrails

- [ ] **GUARD-01**: Enforce experiment count limit
- [ ] **GUARD-02**: Enforce time budget (minutes)
- [ ] **GUARD-03**: Enforce disk space minimum (1GB free)
- [ ] **GUARD-04**: Stop gracefully when any guardrail trips

### Intelligence

- [ ] **INTEL-01**: Compute baselines (naive strategies) before experimentation
- [ ] **INTEL-02**: Baseline gate: model must beat baselines to be kept
- [ ] **INTEL-03**: Diagnostics: analyze worst predictions, bias, feature-error correlations
- [ ] **INTEL-04**: Inject diagnostics into next iteration prompt
- [ ] **INTEL-05**: Multi-draft phase: 3-5 diverse initial solutions, pick best
- [ ] **INTEL-06**: Stagnation detection: N consecutive reverts triggers model family switch
- [ ] **INTEL-07**: Branch-on-stagnation: git branch from best-ever, try different family

### State & Recovery

- [ ] **STATE-01**: Checkpoint saves after every experiment iteration
- [ ] **STATE-02**: Resume from checkpoint after context reset or crash
- [ ] **STATE-03**: Append-only results.jsonl survives partial writes
- [ ] **STATE-04**: Human-readable experiments.md journal updated per iteration

### Tabular Domain

- [ ] **TAB-01**: sklearn, XGBoost, LightGBM model families supported
- [ ] **TAB-02**: Metrics: accuracy, f1, f1_weighted, r2, rmse, mae
- [ ] **TAB-03**: Cross-validation evaluation in train.py
- [ ] **TAB-04**: Tabular-specific baselines (most_frequent, stratified, mean, median)

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

- [ ] **FIN-01**: Export best model artifact with metadata.json sidecar
- [ ] **FIN-02**: Generate retrospective markdown (what worked, what didn't, trajectory)
- [ ] **FIN-03**: Tag best commit in git (ml-best-{run_id})

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
| PROF-01 | Phase 2 | Pending |
| PROF-02 | Phase 2 | Pending |
| PROF-03 | Phase 2 | Pending |
| PROF-04 | Phase 2 | Pending |
| SCAF-01 | Phase 2 | Pending |
| SCAF-02 | Phase 2 | Pending |
| SCAF-03 | Phase 2 | Pending |
| SCAF-04 | Phase 2 | Pending |
| LOOP-01 | Phase 2 | Pending |
| LOOP-02 | Phase 2 | Pending |
| LOOP-03 | Phase 2 | Pending |
| LOOP-04 | Phase 2 | Pending |
| LOOP-05 | Phase 2 | Pending |
| LOOP-06 | Phase 2 | Pending |
| GUARD-01 | Phase 2 | Pending |
| GUARD-02 | Phase 2 | Pending |
| GUARD-03 | Phase 2 | Pending |
| GUARD-04 | Phase 2 | Pending |
| INTEL-01 | Phase 3 | Pending |
| INTEL-02 | Phase 3 | Pending |
| INTEL-03 | Phase 3 | Pending |
| INTEL-04 | Phase 3 | Pending |
| INTEL-05 | Phase 3 | Pending |
| INTEL-06 | Phase 3 | Pending |
| INTEL-07 | Phase 3 | Pending |
| STATE-01 | Phase 2 | Pending |
| STATE-02 | Phase 5 | Pending |
| STATE-03 | Phase 2 | Pending |
| STATE-04 | Phase 2 | Pending |
| TAB-01 | Phase 2 | Pending |
| TAB-02 | Phase 2 | Pending |
| TAB-03 | Phase 2 | Pending |
| TAB-04 | Phase 2 | Pending |
| DL-01 | Phase 4 | Pending |
| DL-02 | Phase 4 | Pending |
| DL-03 | Phase 4 | Pending |
| DL-04 | Phase 4 | Pending |
| FT-01 | Phase 4 | Pending |
| FT-02 | Phase 4 | Pending |
| FT-03 | Phase 4 | Pending |
| FT-04 | Phase 4 | Pending |
| FIN-01 | Phase 2 | Pending |
| FIN-02 | Phase 2 | Pending |
| FIN-03 | Phase 2 | Pending |
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
