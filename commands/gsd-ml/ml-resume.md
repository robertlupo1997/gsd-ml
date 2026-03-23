---
name: gsd:ml-resume
description: Resume an experiment from checkpoint
argument-hint: "[--run <run_id>]"
allowed-tools: [Read, Write, Edit, Bash, Glob, Grep, Task]
---
<objective>Resume a paused or interrupted ML experiment by loading checkpoint state and re-entering the experiment loop.</objective>
<execution_context>@~/.claude/gsd-ml/workflows/ml-resume.md
@~/.claude/gsd-ml/workflows/ml-run.md</execution_context>
<context>Optional --run flag to specify a specific run_id. If omitted, resumes the most recent checkpoint.

Arguments: $ARGUMENTS</context>
<process>Follow the ml-resume workflow to restore state, then continue the experiment loop from ml-run.md Phase 3.</process>
<references>@~/.claude/gsd-ml/references/metric-map.md</references>
