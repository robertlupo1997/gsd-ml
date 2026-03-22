---
name: gsd:ml
description: Run an autonomous ML experiment
argument-hint: "<dataset> <target> [--domain tabular|dl|ft]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---
<objective>Run an autonomous tabular ML experiment: profile dataset, scaffold .ml/ directory, iterate on train.py, export best model.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-run.md</execution_context>
<context>Dataset path: first argument. Target column: second argument. Domain defaults to tabular.

Arguments: $ARGUMENTS</context>
<process>Follow the ml-run workflow step by step. Do not skip phases. Do not modify prepare.py.</process>
<references>@~/.claude/gsd-ml/references/metric-map.md</references>
