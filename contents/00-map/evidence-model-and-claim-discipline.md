---
title: "证据模型：把代码事实与推断分离"
slug: "evidence-model-and-claim-discipline"
summary: "定义 E1/E2/E3 三层证据等级，建立文章结论的可审计标准。"
track: "map"
category: "map"
order: 2
tags: ["evidence", "methodology", "technical-writing"]
level: "advanced"
depth: "L1"
evidence_level: "E1"
code_anchors:
  - path: "claude-code-main/src/query.ts"
    symbols: ["budget checks", "compaction calls"]
  - path: "claude-code-main/src/utils/permissions/filesystem.ts"
    symbols: ["read/write permission order"]
  - path: "claude-code-main/src/services/analytics/growthbook.ts"
    symbols: ["feature gate reads"]
prerequisites: ["architecture-map"]
status: "published"
updatedAt: "2026-04-06"
lang: "zh-CN"
translation_of: null
---

# 证据模型：把代码事实与推断分离

> 这篇是整站的“防跑偏机制”。  
> 没有证据级别，文章很容易从工程分析滑向“高质量主观感受”。

## 1. 为什么必须有证据模型

如果你在团队里做过技术评审，会发现一个常见现象：  
同样一段代码，A 说“这里是稳定性设计”，B 说“这里只是历史包袱”。  
争论本身没问题，问题是**双方都拿不出可复查的证据链**。

因此我们把结论分层，不再用“语气强度”代表“事实强度”。

## 2. E1 / E2 / E3 的定义

### E1：直接代码证据

在同一个文件内可以直接看到行为依据。  
例如：某个分支先判 deny，再判 allow。

### E2：跨文件行为证据

单文件看不全，但通过调用链可以闭环验证。  
例如：`query.ts` 触发压缩，`autoCompact.ts` 决定阈值和断路。

### E3：带前提推断

代码没有直接表达，需要结合上下文推断。  
此时必须写清前提和不确定性，不能伪装成事实。

## 3. 一个实际判定示例

假设我们要写结论：  
“权限系统真正边界在判定顺序，不在 UI 弹窗。”

可以这样落证据：

```text
E1: filesystem.ts 中 read/write 判定顺序是固定链条
E2: permissionSetup.ts 对危险规则做前置拦截
E3: 在团队默认配置下，这种顺序更适合共享工作区
```

这样写的好处是：读者能精确知道哪部分是事实、哪部分是判断。

## 4. 写作时的最小流程

每个关键结论都走四步：

1. 先找锚点文件。
2. 再写观察事实。
3. 再给证据等级。
4. 最后给设计解释。

你会发现这和“先有观点再找证据”正好反过来。  
这就是质量差异的来源。

## 5. 常见误用（也是最容易翻车的地方）

### 误用 1：把 E3 写成 E1

典型句式：  
“作者显然是想……”  
这种句子如果没有注释或分支证据，就是推断，不是事实。

### 误用 2：只有模块名，没有定位

只写 “在权限模块里” 没意义。  
至少要给路径级锚点，例如 `src/utils/permissions/filesystem.ts`。

### 误用 3：跨文件行为没闭环

只看到调用点，不看被调用实现，就急着下结论。  
这会让 E2 退化成“猜测拼图”。

## 6. 为什么这套约束值回成本

证据标注会增加编辑成本，这是真的。  
但它带来三个直接收益：

- 团队讨论可回到同一组事实。
- 新人接手时不需要猜作者意图。
- 文章可以直接进入架构评审材料，而不是只能当博客看。

## 7. 一个建议的段落写法

你可以用这个固定句式：

```markdown
结论：……
证据等级：E1/E2/E3
代码锚点：……
边界条件：……
```

用几次后，你会明显感觉文章质量更稳定。

## 8. 下一步

接下来先读 `runtime-entry-and-turn-lifecycle`。  
那篇会直接演示：如何在机制文中把证据规则落到完整运行链路里。

