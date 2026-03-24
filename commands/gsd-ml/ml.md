---
name: gsd:ml
description: Run an autonomous ML experiment — profile data, train models, iterate, and export the best result. Supports tabular (sklearn/XGBoost/LightGBM), deep learning (image/text), and fine-tuning (LoRA/QLoRA).
argument-hint: "<dataset> <target> [--domain tabular|dl|ft] [--task <task_type>] [--model-name <model>]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---
<objective>Run an autonomous ML experiment: profile dataset, scaffold .ml/ directory, iterate on train.py, export best model. Supports tabular (sklearn/XGBoost/LightGBM), deep learning (timm/transformers), and fine-tuning (LoRA/QLoRA) domains.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-run.md</execution_context>
<context>Dataset path: first argument. Target column: second argument (optional for image classification). Domain defaults to tabular. Use --domain dl for deep learning, --domain ft for fine-tuning. Use --task for DL subtask (image_classification, text_classification). Use --model-name for FT base model.

Arguments: $ARGUMENTS</context>
<process>Follow the ml-run workflow step by step. Do not skip phases. Do not modify prepare.py.</process>
<references>@~/.claude/gsd-ml/references/metric-map.md</references>
