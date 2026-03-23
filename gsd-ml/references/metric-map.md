# Metric Map: Tabular ML

Reference mapping metric names to sklearn scoring strings, task types, and optimization direction.

The `profiler.profile_dataset()` function auto-selects the metric based on the target column's characteristics, so this reference is primarily for Claude Code's understanding when interpreting results (e.g., knowing that rmse is "lower is better").

## Metric Table

| Metric | sklearn scoring | Task | Direction |
|--------|----------------|------|-----------|
| accuracy | accuracy | classification | maximize |
| f1 | f1 | binary classification | maximize |
| f1_weighted | f1_weighted | multiclass classification | maximize |
| r2 | r2 | regression | maximize |
| rmse | neg_root_mean_squared_error | regression | minimize |
| mae | neg_mean_absolute_error | regression | minimize |

## Direction Notes

- **maximize**: Higher values are better. A new experiment improves if `new_score > best_score`.
- **minimize**: Lower values are better. For sklearn scoring, these use `neg_` prefix (the actual score returned is negative, so sklearn can always maximize internally). When comparing raw metric values (not sklearn scores), compare as `new_score < best_score`.

## Metric Selection Logic

The profiler auto-selects metrics using this logic:
- **Binary classification** (2 unique target values): `f1`
- **Multiclass classification** (3-20 unique target values): `f1_weighted`
- **Regression** (>20 unique values or float target): `r2`

The `accuracy` metric is available but not auto-selected (f1 variants are more informative for imbalanced classes). The `rmse` and `mae` metrics are alternatives to `r2` for regression tasks.

## Deep Learning Metrics

| Metric | Task | Direction |
|--------|------|-----------|
| accuracy | image/text classification | maximize |
| f1_weighted | text classification | maximize |
| loss | any DL task | minimize |

### DL Metric Selection Logic

- **Image classification**: defaults to `accuracy`
- **Text classification**: defaults to `f1_weighted`
- `loss` is always available as an alternative metric for any DL task

## Fine-Tuning Metrics

| Metric | Task | Direction |
|--------|------|-----------|
| perplexity | causal LM | minimize |
| loss | any FT task | minimize |
| rouge1 | instruction following / summarization | maximize |
| rougeL | instruction following / summarization | maximize |

### FT Metric Defaults

- **Default metric**: `perplexity` (lower is better, measures model confidence)
- `loss` is the raw cross-entropy loss (lower is better)
- `rouge1` and `rougeL` measure generation quality against reference outputs (higher is better)
- For instruction-tuning tasks with reference outputs, prefer ROUGE metrics
