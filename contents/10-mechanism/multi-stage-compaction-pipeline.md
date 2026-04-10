---
title: "多阶段上下文压缩管线"
slug: "multi-stage-compaction-pipeline"
summary: "拆解 snip、microcompact、autocompact 与 session memory compact 的触发顺序与断路机制。"
track: "mechanism"
category: "mechanism"
order: 15
tags: ["compaction", "context", "reliability", "circuit-breaker"]
level: "advanced"
depth: "L2"
evidence_level: "E1"
code_anchors:
  - path: "claude-code-main/src/query.ts"
    symbols: ["snip", "microcompact", "autocompact call order"]
  - path: "claude-code-main/src/services/compact/autoCompact.ts"
    symbols: ["threshold", "failure breaker"]
  - path: "claude-code-main/src/services/compact/compact.ts"
    symbols: ["compaction flow"]
  - path: "claude-code-main/src/services/compact/sessionMemoryCompact.ts"
    symbols: ["session memory branch"]
prerequisites: ["context-budget-and-tool-result-storage"]
status: "published"
updatedAt: "2026-04-06"
lang: "zh-CN"
translation_of: null
---

# 多阶段上下文压缩管线

> “压缩”听起来像一个动作，生产系统里它其实是一条连续控制链。  
> 这条链处理的不只是 token 数量，还处理失败恢复与语义保真。

## 1. 为什么单步压缩一定会撞墙

很多第一版实现是：

```python
if tokens > threshold:
    messages = summarize(messages)
```

这在短会话可能够用，但在工具密集长会话里会遇到两个问题：

- 压缩力度太弱：压不下来。
- 压缩力度太强：关键信息被抹平。

所以必须做分阶段，而不是单阶段。

## 2. 在源码里看压缩链条

从 `claude-code-main/src/query.ts` 到 `services/compact/*`，可以看到清晰分层：

1. `snip`：低成本裁剪，优先保留结构。
2. `microcompact`：中强度压缩，处理局部膨胀。
3. `autocompact`：高压阈值下的自动压缩。
4. `sessionMemoryCompact`：面向会话记忆边界的专项路径。

这四层对应四种压力状态，而不是“同一个函数的四个参数”。

## 3. 断路器为什么是必须项

`claude-code-main/src/services/compact/autoCompact.ts` 的断路逻辑解决的是一个真实风险：  
压缩本身也会失败，如果失败后盲目重试，系统会进入压缩风暴。

示意：

```text
超压 -> 压缩失败 -> 继续超压 -> 再压缩失败 -> ...
```

没有断路器时，这条链不会自然收敛。

## 4. 压缩成功不等于系统可用

这是很容易被忽略的一点。  
压缩成功只说明 token 下降，不说明状态可用。

真正需要确认的是：

- 任务目标是否仍清晰。
- 工具结果引用是否仍可追溯。
- 下一轮是否还能做正确决策。

如果这些没保住，系统只是“活着”，不是“工作着”。

## 5. session memory branch 的意义

`sessionMemoryCompact.ts` 代表一个关键工程判断：  
会话记忆和普通消息不能完全同策略处理。

原因很简单：

- 会话记忆包含跨轮决策线索。
- 这些线索一旦丢失，后续行为会看起来“突然变笨”。

所以单独分支不是复杂化，而是保边界。

## 6. 一条可执行的压缩治理建议

你可以按这个顺序落地：

1. 先加入口预算检查。
2. 再加 `snip` + `microcompact`。
3. 再加 `autocompact` 与断路计数。
4. 最后再处理 session memory 专项策略。

不要反过来。先把基础层做稳，再做高级层。

## 7. 常见事故信号

以下信号出现两个以上，就该检查压缩管线：

- 单回合压缩触发次数异常上升。
- 压缩后工具重试率明显上升。
- 会话后半段回答一致性明显下降。

这些往往不是模型退化，而是压缩策略失配。

## 8. 小结

多阶段压缩的核心不是“更聪明地摘要”，而是：  
**把上下文压力控制从一次性操作升级为可治理流程。**

## Next Read
- `why-query-loop-owns-control-plane`
- `build-a-minimal-query-loop`

