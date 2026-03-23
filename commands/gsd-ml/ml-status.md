---
name: gsd:ml-status
description: Show experiment run status and metrics
argument-hint: "[--detail <run_id>]"
allowed-tools: [Read, Bash, Glob]
---
<objective>Show a summary of experiment runs from .ml/ directory, or a detailed view with ASCII metric trajectory for a specific run.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-status.md</execution_context>
<context>Arguments: $ARGUMENTS</context>
<process>Follow the ml-status workflow step by step.</process>
