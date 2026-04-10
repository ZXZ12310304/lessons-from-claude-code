---
title: Why Query Loop must assume control plane
slug: why-query-loop-owns-control-plane
summary: Justify that centralizing retries, budgeting, tool injection, and compaction coordination in the query loop is architectural
  design, not a bad smell.
track: decision
category: decision
order: 20
tags:
- decision
- control-plane
- orchestration
level: advanced
depth: L3
evidence_level: E2
code_anchors:
- path: claude-code-main/src/query.ts
  symbols:
  - orchestration timeline
  - budget/retry/compact integration
- path: claude-code-main/src/QueryEngine.ts
  symbols:
  - session ownership
prerequisites:
- query-loop-state-machine-and-continue-transitions
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: why-query-loop-owns-control-plane
---

# Why Query Loop must assume control plane

> This article discusses a controversial issue:
> `query.ts` looks heavy, why not take it apart completely?

## 1. Acknowledge your intuition first: it’s indeed “big”

Judging from the look and feel of the code, everyone’s first reaction is usually right:
The `query` layer carries too much logic and looks like a "God function".

But in the agent runtime, judging whether it is good or bad cannot just look at the length of the file, but also whether the control rights are clear.
If splitting leads to splitting of control, the system changes from "complex but controllable" to "elegant but uncontrollable".

## 2. Definition of control plane

The control plane mentioned here is not a control plane in the sense of infrastructure.
In this project, it means:

- Who decides whether to continue or quit this round.
- Who decides when the budget checks.
- Who decides when tool results are back-injected.
- Who decides retry and compaction priorities.

If these decisions are spread across multiple modules, timing conflicts can occur.

## 3. Why the concentration on `query.ts` is intentional

From `claude-code-main/src/query.ts` we can see:
Budgets, tools, compression, and retries all advance around the same round of state.

If you split them into "independent services", three types of problems will usually occur:

1. Each module "thinks it is the main process".
2. Shared state becomes implicitly coupled.
3. Accident troubleshooting requires splicing multiple timelines.

The cost of centralized control is increased local complexity, and the benefit is consistent global behavior.

## 4. When should it be dismantled and when should it not be dismantled?

What can be dismantled is capability, but what should not be dismantled is sovereignty.

### should be dismantled

- Tool implementation details
- Compression algorithm implementation
- Permission check implementation

### Should not be dismantled

- turn transfer sovereignty
- Exit Judgment Sovereignty
- Budget trigger timing sovereignty

In a word: ** capabilities can be modularized, and timing control must be centralized. **

## 5. A common counterexample

The counterexample structure usually looks like this:

```text
RetryService 决定重试
CompactService 决定压缩
ToolService 决定回注时机
QueryService 只做转发
```

This looks elegantly layered, but in actual operation there will be a "wait for each other + overwrite each other" conflict.
In the end, anyone can change the status, and no one is responsible for the results.

## 6. How to retain centralized control and prevent code from getting out of control

You can use this compromise strategy:

- Preserve state machines and sequential decisions at the `query` level.
- Downgrade replaceable algorithms into pure capability modules.
- Record input and output contracts for each capability invocation.

Doing so keeps sovereignty centralized while layering implementation complexity.

## 7. Judgment criteria during review

When you discuss "whether to split the query layer" in the team, don't just look at the volume, focus on three things:

1. Who has the final exit judgment after demolition?
2. Will the status writing still converge at a single point after the disassembly?
3. Can a single time series log be maintained after disassembly?

If you can't answer one of the three questions clearly, don't open it yet.

## 8. Summary

What I want to emphasize in this article is:
`query` Heavy layers are not necessarily a bad taste;
In many agent systems, it is the control plane intentionally responsible for cross-domain arbitration.

## Next Read
- `why-permission-check-order-is-boundary`
- `build-a-minimal-query-loop`
