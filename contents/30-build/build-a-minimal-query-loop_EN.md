---
title: Rebuild a minimal usable Query Loop
slug: build-a-minimal-query-loop
summary: 'Provide the minimum main loop implementation that can be implemented: budget check, tool round, exit submission,
  retry guardrail.'
track: build
category: build
order: 30
tags:
- build
- implementation
- query-loop
level: intermediate
depth: L3
evidence_level: E2
code_anchors:
- path: claude-code-main/src/query.ts
  symbols:
  - loop skeleton
- path: claude-code-main/src/services/tools/toolOrchestration.ts
  symbols:
  - tool dispatch
- path: claude-code-main/src/services/compact/autoCompact.ts
  symbols:
  - compaction threshold
prerequisites:
- runtime-entry-and-turn-lifecycle
- tool-contract-and-dispatch-pipeline
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: build-a-minimal-query-loop
---

# Rebuild a minimal usable Query Loop

> This article does not talk about the "ideal architecture", only the smallest version that "can be built within a week and will not turn over immediately".

## 1. What the minimum usable version must contain

If you have limited time, the minimum closed loop must have at least four blocks:

1. Session state object (can be persisted across rounds).
2. query loop (can handle continue).
3. Tool distribution (can run the tool call and back-note).
4. Budget check (can avoid the round directly exceeding the window).

If any piece is missing, it is not "minimum usable", but "demo code".

## 2. The first version of the skeleton code

```python
while True:
    ctx = build_context(session)
    enforce_budget(ctx)

    step = call_model(ctx)
    if step.tool_calls:
        results = run_tools(step.tool_calls)
        session = append_tool_results(session, results)
        continue

    session = commit_assistant_output(session, step.output)
    break
```

The point of this skeleton is not "simple", but that it already has a closed loop.

## 3. Three engineering constraints that need to be addressed on the first day

### Constraint A: Separation of submission and display

Streaming output can be displayed first, but final commit must occur at a single point.
Otherwise, it will be easy to fail to keep up with history during recovery.

### Constraint B: Tool back-annotation must be structured

The tool output cannot be spliced ​​into history as a piece of free text.
At least the tool name, call parameters, result summary, and result reference must be included.

### Constraint C: Budget check must be preceded

Post-budget means that you have already paid the cost and then find that the limit is exceeded, which is a passive stop loss.

## 4. What should be added in the second stage (don’t do it all at the beginning)

建议按这个顺序迭代：

1. Retry strategy (recoverable).
2. Authority assessment (governability).
3. Staged compression (sustainable).

Don’t use complex memory systems and multiple agents at the beginning. Make the single loop stable first.

## 5. A practical directory suggestion

```text
src/
  runtime/
    query_loop.py
    session_state.py
  tools/
    contracts.py
    orchestrator.py
  safety/
    permissions.py
    budget.py
```

目录不重要，重要的是“主权收敛”：回合状态在一个地方收敛提交。

## 6. Verify whether this version is actually available

It is enough to do three sets of tests:

- Whether the status of the tool branch is consistent for three consecutive rounds of calls.
- Whether the simulation overwindow triggers budget control and continues to run.
- Whether the simulation can be restored to the correct round after being interrupted and restarted.

If you pass three groups, add additional functions; if you pass three groups, don't add functions.

## 7. Common symptoms of “It looks like it can run, but it actually doesn’t work”

- A new session object is created every round.
- After the tool fails, it is discarded directly without recording the status.
- The budget logic only prompts in the log and does not actually control the process.

These problems are not painful in the early stage, but will be very painful after the flow increases.

## 8. Summary

The core of the smallest available query loop is not "less code", but "complete closed loop".
Only when the closed loop is complete can it withstand subsequent complexity.

## Next Read
- `build-a-safe-tool-runtime`
