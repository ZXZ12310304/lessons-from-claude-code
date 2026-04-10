---
title: "为什么权限判定顺序本身就是安全边界"
slug: "why-permission-check-order-is-boundary"
summary: "说明 deny/ask/allow 的评估顺序为何比弹窗文案更关键，以及如何防止隐性提权。"
track: "decision"
category: "decision"
order: 21
tags: ["decision", "permissions", "security-boundary"]
level: "advanced"
depth: "L3"
evidence_level: "E2"
code_anchors:
  - path: "claude-code-main/src/utils/permissions/filesystem.ts"
    symbols: ["read order", "write order"]
  - path: "claude-code-main/src/utils/permissions/permissionSetup.ts"
    symbols: ["unsafe rule lint"]
prerequisites: ["permissions-runtime-evaluation"]
status: "published"
updatedAt: "2026-04-06"
lang: "zh-CN"
translation_of: null
---

# 为什么权限判定顺序本身就是安全边界

> 这篇不是“权限机制怎么写”，而是“为什么判定顺序就是边界本体”。  
> 顺序错了，配置再多都可能是错位保护。

## 1. 从一个真实决策冲突出发

产品常会提出需求：  
“把这个命令默认放行，别总弹窗了。”

安全会提出反需求：  
“这个命令必须先过 deny 规则，不能先看 allow。”

这其实不是体验 vs 安全的简单冲突，而是“顺序是否可被破坏”的冲突。

## 2. 为什么顺序比规则数量更关键

假设你有 20 条规则，但顺序不稳定。  
那系统就会在不同路径命中不同优先级，行为不可预测。

`claude-code-main/src/utils/permissions/filesystem.ts` 显示的核心思想是：  
先定义顺序契约，再允许规则扩展。

一个可靠链条通常是：

```text
hard deny -> ask -> explicit allow -> implicit default
```

## 3. 顺序就是“可证明性”

如果团队问：“为什么这次放行了？”  
你需要能回答：

1. 命中了哪条规则。
2. 为什么前面的更强规则没有命中。
3. 最终决策是否经过附加安全检查。

这三件事只有在顺序稳定时才可证明。

## 4. 为什么“用户点了同意”不能成为终局

很多实现会把用户确认视为最终裁决。  
但生产系统里，用户确认应该是链条中的一个步骤，不是跳过链条的后门。

尤其是写操作和 shell 执行，仍应受结构性安全检查约束。  
否则会出现“用户误触 + 系统全放行”的组合风险。

## 5. 配置加载阶段的防线不能省

`claude-code-main/src/utils/permissions/permissionSetup.ts` 体现了另一个关键决策：  
危险规则要在加载时就被发现，而不是运行时碰运气。

这类前置 lint 的价值是把风险提前，从执行风险变成配置风险。

## 6. 常见反模式

### 反模式 A：按功能模块各自定义顺序

文件系统一套、shell 一套、MCP 一套。  
最后用户和开发者都无法建立统一预期。

### 反模式 B：插入“特例捷径”

为了某个场景快速上线，在链条中插入一条“先 allow 再说”。  
短期省事，长期是审计灾难。

### 反模式 C：日志只记结论不记路径

只记 `allowed=true`，不记命中规则链，复盘几乎无法进行。

## 7. 工程建议：把顺序当 API

一旦确定优先级顺序，就把它当公开契约：

- 写测试保证顺序不回归。
- 写文档说明每一层职责。
- 写日志输出命中路径。

这比“再加一层弹窗”更能提升真实安全性。

## 8. 小结

权限系统的“边界”不是某条规则，也不是某个按钮。  
边界是规则运行的顺序与不可绕过性。

## Next Read
- `build-a-safe-tool-runtime`
