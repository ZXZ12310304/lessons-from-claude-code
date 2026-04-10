---
title: "复建一个最小可用 Query Loop"
slug: "build-a-minimal-query-loop"
summary: "给出可落地的最小主循环实现：预算检查、工具回合、退出提交、重试护栏。"
track: "build"
category: "build"
order: 30
tags: ["build", "implementation", "query-loop"]
level: "intermediate"
depth: "L3"
evidence_level: "E2"
code_anchors:
  - path: "claude-code-main/src/query.ts"
    symbols: ["loop skeleton"]
  - path: "claude-code-main/src/services/tools/toolOrchestration.ts"
    symbols: ["tool dispatch"]
  - path: "claude-code-main/src/services/compact/autoCompact.ts"
    symbols: ["compaction threshold"]
prerequisites: ["runtime-entry-and-turn-lifecycle", "tool-contract-and-dispatch-pipeline"]
status: "published"
updatedAt: "2026-04-06"
lang: "zh-CN"
translation_of: null
---

# 复建一个最小可用 Query Loop

> 这篇不讲“理想架构”，只讲“可以一周内做出来并且不至于马上翻车”的最小版本。

## 1. 最小可用版本必须包含什么

如果你时间有限，最小闭环至少要有四块：

1. 会话状态对象（能跨轮保留）。
2. query loop（能处理 continue）。
3. 工具分发（能把 tool call 跑完并回注）。
4. 预算检查（能避免回合直接超窗）。

缺任何一块，都不是“最小可用”，而是“演示代码”。

## 2. 第一版骨架代码

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

这个骨架的重点不是“简单”，而是它已经具备了回合闭环。

## 3. 三个第一天就要做的工程约束

### 约束 A：提交与展示分离

流式输出可以先显示，但最终提交必须单点发生。  
否则恢复时很容易对不上历史。

### 约束 B：工具回注必须结构化

不能把工具输出当一段自由文本拼接进历史。  
至少要有工具名、调用参数、结果摘要、结果引用。

### 约束 C：预算检查必须前置

预算后置意味着你已经付出成本再发现超限，属于被动止损。

## 4. 第二阶段该加什么（不要一上来全做）

建议按这个顺序迭代：

1. 重试策略（可恢复）。
2. 权限评估（可治理）。
3. 分阶段压缩（可持续）。

不要一开始就上复杂记忆系统和多 agent，先把单循环做稳。

## 5. 一个实用目录建议

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

## 6. 验证这版是否真的可用

做三组测试就够：

- 工具分支连续三轮调用是否状态一致。
- 模拟超窗是否会触发预算控制并继续运行。
- 模拟中断重启后是否能恢复到正确回合。

三组都过，再加功能；三组不过，不要扩功能。

## 7. 常见“看起来能跑，实际上不可用”的征兆

- 每轮都新建 session 对象。
- 工具失败后直接丢弃，不记入状态。
- 预算逻辑只在日志里提示，不真正控制流程。

这些问题早期不痛，流量上来后会很痛。

## 8. 小结

最小可用 query loop 的核心不是“代码少”，而是“闭环完整”。  
闭环完整，才能承受后续复杂度。

## Next Read
- `build-a-safe-tool-runtime`
