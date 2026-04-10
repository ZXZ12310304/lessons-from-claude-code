---
title: Multi-stage context compression pipeline
slug: multi-stage-compaction-pipeline
summary: Disassemble the trigger sequence and circuit breaking mechanism of snip, microcompact, autocompact and session memory
  compact.
track: mechanism
category: mechanism
order: 15
tags:
- compaction
- context
- reliability
- circuit-breaker
level: advanced
depth: L2
evidence_level: E1
code_anchors:
- path: claude-code-main/src/query.ts
  symbols:
  - snip
  - microcompact
  - autocompact call order
- path: claude-code-main/src/services/compact/autoCompact.ts
  symbols:
  - threshold
  - failure breaker
- path: claude-code-main/src/services/compact/compact.ts
  symbols:
  - compaction flow
- path: claude-code-main/src/services/compact/sessionMemoryCompact.ts
  symbols:
  - session memory branch
prerequisites:
- context-budget-and-tool-result-storage
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: multi-stage-compaction-pipeline
---

# Multi-stage context compression pipeline

> "Compression" sounds like an action, but in a production system it is actually a continuous control chain.
> This chain handles not only the number of tokens, but also failure recovery and semantic fidelity.

## 1. Why single-step compression will definitely hit a wall

Many first version implementations were:

```python
if tokens > threshold:
    messages = summarize(messages)
```

This may work in short sessions, but in tool-intensive long sessions you will encounter two problems:

- The compression force is too weak: it cannot be compressed.
- Compression is too strong: key information is obliterated.

So it must be done in stages rather than in a single stage.

## 2. View the compression chain in the source code

From `claude-code-main/src/query.ts` to `services/compact/*`, you can see clear layering:

1. `snip`: Low-cost cutting, giving priority to preserving the structure.
2. `microcompact`: Medium intensity compression, handling local expansion.
3. `autocompact`: Automatic compression at high pressure threshold.
4. `sessionMemoryCompact`: Specialized paths for session memory boundaries.

These four layers correspond to four pressure states, rather than "four parameters of the same function".

## 3. Why is a circuit breaker necessary?

The circuit breaking logic of `claude-code-main/src/services/compact/autoCompact.ts` solves a real risk:
Compression itself will also fail. If you blindly retry after failure, the system will enter a compression storm.

Indicate:

```text
超压 -> 压缩失败 -> 继续超压 -> 再压缩失败 -> ...
```

Without circuit breakers, the chain will not naturally converge.

## 4. Successful compression does not mean that the system is usable

This is something that is easily overlooked.
Successful compression only indicates that the token has declined, but does not indicate that the status is available.

What really needs to be confirmed is:

- Is the mission objective still clear?
- Whether tool result references are still traceable.
- Can we still make the right decision in the next round?

If these are not maintained, the system is only "alive", not "working".

## 5. The meaning of session memory branch

`sessionMemoryCompact.ts` represents a critical engineering judgment:
Conversation memories and ordinary messages cannot be handled exactly the same way.

The reason is simple:

- Conversational memory contains cross-turn decision cues.
- Once these cues are lost, subsequent behavior can appear "suddenly stupid."

Therefore, separate branches do not complicate things, but preserve boundaries.

## 6. An executable compression governance recommendation

You can land in this order:

1. First add the import budget check.
2. Add `snip` + `microcompact`.
3. Add `autocompact` and the break count.
4. Finally, we will deal with the session memory special strategy.

Don't do it the other way around. Make the basic layer stable first, and then build the advanced layer.

## 7. Common accident signals

If more than two of the following signals appear, it is time to check the compression pipeline:

- The number of compression triggers in a single round increased abnormally.
- The tool retry rate increased significantly after compression.
- Response consistency dropped significantly in the second half of the session.

These are often not model degradations, but compression strategy mismatches.

## 8. Summary

The core of multi-stage compression is not "smarter summarization", but:
**Upgrade contextual pressure control from a one-time operation to a manageable process. **

## Next Read
- `why-query-loop-owns-control-plane`
- `build-a-minimal-query-loop`
