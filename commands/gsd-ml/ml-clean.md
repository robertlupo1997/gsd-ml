---
name: gsd:ml-clean
description: Remove experiment state and optionally git branches
argument-hint: "[--branches] [--force]"
allowed-tools: [Read, Bash, Glob]
---
<objective>Remove .ml/ experiment directory after showing a preview and confirming with the user. Optionally clean up ml/run-* branches and ml-best-* tags.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-clean.md</execution_context>
<context>Arguments: $ARGUMENTS</context>
<process>Follow the ml-clean workflow step by step. Always preview before deleting. Always confirm unless --force.</process>
