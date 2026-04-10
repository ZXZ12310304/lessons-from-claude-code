---
title: "为什么 Query Loop 必须承担控制平面"
slug: "why-query-loop-owns-control-plane"
summary: "论证将重试、预算、工具回注与压缩协调集中在 query loop 是有意架构，而非坏味道。"
track: "decision"
category: "decision"
order: 20
tags: ["decision", "control-plane", "orchestration"]
level: "advanced"
depth: "L3"
evidence_level: "E2"
code_anchors:
  - path: "claude-code-main/src/query.ts"
    symbols: ["orchestration timeline", "budget/retry/compact integration"]
  - path: "claude-code-main/src/QueryEngine.ts"
    symbols: ["session ownership"]
prerequisites: ["query-loop-state-machine-and-continue-transitions"]
status: "published"
updatedAt: "2026-04-06"
lang: "zh-CN"
translation_of: null
---

# 为什么 Query Loop 必须承担控制平面

> 这篇讨论一个容易引发争议的问题：  
> `query.ts` 看起来很重，为什么不彻底拆散？

## 1. 先承认直觉：它确实“很大”

从代码观感看，大家的第一反应通常是对的：  
`query` 层承载了太多逻辑，看起来像“上帝函数”。

但在 agent runtime 里，判断好坏不能只看文件长度，要看控制权是否清晰。  
如果拆分导致控制权分裂，系统会从“复杂但可控”变成“优雅但不可控”。

## 2. 控制平面的定义

这里说的控制平面，不是基础设施意义上的 control plane。  
在这个项目里，它指的是：

- 谁决定本轮继续还是退出。
- 谁决定何时预算检查。
- 谁决定工具结果何时回注。
- 谁决定重试和压缩优先级。

这些决定如果分散到多个模块，就会出现时序冲突。

## 3. 为什么集中在 `query.ts` 是有意设计

从 `claude-code-main/src/query.ts` 可以看到：  
预算、工具、压缩、重试都围绕同一轮状态推进。

如果把它们拆成“各自独立服务”，通常会出现三类问题：

1. 每个模块都在“以为自己是主流程”。
2. 共享状态变成隐式耦合。
3. 事故排查需要拼接多条时间线。

集中控制的代价是局部复杂度上升，收益是全局行为一致。

## 4. 什么时候应该拆，什么时候不该拆

可以拆的是能力，不该拆的是主权。

### 应该拆

- 工具执行细节
- 压缩算法实现
- 权限检查实现

### 不该拆

- 回合迁移主权
- 退出判定主权
- 预算触发时机主权

一句话：**能力可以模块化，时序主权要集中。**

## 5. 一个常见反例

反例结构通常长这样：

```text
RetryService 决定重试
CompactService 决定压缩
ToolService 决定回注时机
QueryService 只做转发
```

这看起来分层优雅，实际运行时会出现“互相等待 + 互相覆盖”的冲突。  
最终谁都能改状态，谁都不对结果负责。

## 6. 如何保留集中控制又避免代码失控

你可以采用这个折中策略：

- 在 `query` 层保留状态机与顺序裁决。
- 把可替换算法下沉为纯能力模块。
- 为每个能力调用记录输入输出契约。

这样做能保持主权集中，同时把实现复杂度分层。

## 7. 评审时的判断标准

当你在团队里讨论“要不要拆 query 层”，不要只看体积，重点看三件事：

1. 拆完后谁拥有最终退出判定？
2. 拆完后状态写入是否仍单点收敛？
3. 拆完后能否保持单一时序日志？

三条里有一条答不清，就先别拆。

## 8. 小结

这篇想强调的是：  
`query` 层重，不一定是坏味道；  
在很多 agent 系统里，它是**有意承担跨域裁决职责**的控制平面。

## Next Read
- `why-permission-check-order-is-boundary`
- `build-a-minimal-query-loop`

