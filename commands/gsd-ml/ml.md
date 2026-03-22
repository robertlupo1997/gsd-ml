---
name: gsd:ml
description: Run an autonomous ML experiment
argument-hint: "<dataset> <target> [--domain tabular|dl|ft]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---
<objective>Run an autonomous ML experiment.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-run.md</execution_context>
<context>Dataset: $ARGUMENTS</context>
<process>Execute the ml-run workflow end-to-end.</process>
