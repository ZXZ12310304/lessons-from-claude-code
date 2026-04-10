---
title: Build safe and controllable tool runtimes
slug: build-a-safe-tool-runtime
summary: 'A tool runtime list is given from an implementation perspective: contract constraints, permission gateways, concurrency
  control, and result governance.'
track: build
category: build
order: 31
tags:
- build
- tool-runtime
- safety
- policy
level: advanced
depth: L3
evidence_level: E2
code_anchors:
- path: claude-code-main/src/Tool.ts
  symbols:
  - tool contract fields
- path: claude-code-main/src/utils/permissions/filesystem.ts
  symbols:
  - policy evaluation
- path: claude-code-main/src/services/tools/StreamingToolExecutor.ts
  symbols:
  - execution streaming
prerequisites:
- tool-contract-and-dispatch-pipeline
- why-permission-check-order-is-boundary
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: build-a-safe-tool-runtime
---

# Build safe and controllable tool runtimes

> The tool runtime is a high-risk area for coding agent accidents. Let’s put up guardrails first, and then talk about capacity expansion.

## 1. Four-layer minimum architecture

```mermaid
graph TD
  A[契约层 Contract] --> B[权限层 Policy Gate]
  B --> C[调度层 Orchestrator]
  C --> D[执行层 Executor]
  D --> E[结果治理 Result Budget]
  E --> F[回注 Query Loop]
```

The loss of any one of these six nodes will directly amplify the probability of failure.

## 2. Contract layer

每个工具必须至少声明：

- `inputSchema`
- `isReadOnly`
- `isConcurrencySafe`
- `maxResultSize`

Without a contract, the subsequent strategy layer cannot make deterministic judgments.

## 3. Permission level

Fixed strategy determination before execution:

```text
schema 校验 -> deny/ask/allow -> 附加安全检查 -> 执行
```

The key points are "before execution" and "cannot be bypassed".

## 4. Scheduling layer

The default is serial, and concurrency is released according to the contract:

- Reading tools prioritize concurrency.
- Write tools exclusively for batches.
- High-risk tools are approved separately.

## 5. Execution layer

Introducing streaming events (progress/result/error) has three values:

1. Visible to the user.
2. Debugging is visible.
3. Interrupts are visible.

## 6. Results governance layer

Don't put large results directly back into the context, change it to "external + reference".
Otherwise the more successful the tool becomes, the more crowded the context becomes and the more degraded the subsequent reasoning becomes.

## 7. Check before going online

- Whether concurrent writing tools are blocked correctly.
- Whether the permission conflict scenario is reproducible stably.
- Whether large results can be read back by reference.
- Whether the state is recoverable after an interruption.

## 8. Summary

When running security tools, it is not about "adding a few more ifs", but connecting contracts, permissions, scheduling, execution, and result management into an auditable chain.

## Next Read
- `multi-stage-compaction-pipeline`
