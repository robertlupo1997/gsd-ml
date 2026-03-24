---
name: gsd:ml-diagnose
description: Diagnose the best model from the last experiment — worst predictions, bias analysis, and confusion matrix
argument-hint: ""
allowed-tools: [Read, Write, Bash, Glob]
---
<objective>Check out the best model from the last experiment, run diagnostics (worst predictions, bias analysis, confusion), and print formatted results with suggested actions.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-diagnose.md</execution_context>
<context>Arguments: $ARGUMENTS</context>
<process>Follow the ml-diagnose workflow step by step. Always save and restore git state.</process>
