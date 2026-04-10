---
title: 'Evidence model: Separating code facts from inference'
slug: evidence-model-and-claim-discipline
summary: Define the three levels of evidence E1/E2/E3 and establish auditable standards for the conclusion of the article.
track: map
category: map
order: 2
tags:
- evidence
- methodology
- technical-writing
level: advanced
depth: L1
evidence_level: E1
code_anchors:
- path: claude-code-main/src/query.ts
  symbols:
  - budget checks
  - compaction calls
- path: claude-code-main/src/utils/permissions/filesystem.ts
  symbols:
  - read/write permission order
- path: claude-code-main/src/services/analytics/growthbook.ts
  symbols:
  - feature gate reads
prerequisites:
- architecture-map
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: evidence-model-and-claim-discipline
---

# Evidence model: Separating code facts from inference

> This article is the "anti-deviation mechanism" of the entire site.
> Without the level of evidence, the article can easily slide from engineering analysis to "high quality subjective feelings".

## 1. Why an evidence model is necessary

If you have done a technical review in your team, you will find a common phenomenon:
For the same piece of code, A says "This is a stability design" and B says "This is just historical baggage".
There is nothing wrong with the argument itself, but the problem is that neither side can produce a re-examineable chain of evidence.

Therefore, we hierarchize the conclusions and no longer use “tone strength” to represent “fact strength”.

## 2. Definition of E1 / E2 / E3

### E1: Direct code evidence

The basis for the behavior can be seen directly in the same file.
For example: a branch is judged to deny first and then to allow.

### E2: Evidence of cross-file behavior

The entire file cannot be viewed in a single file, but it can be verified in a closed loop through the call chain.
For example: `query.ts` triggers compression, `autoCompact.ts` determines thresholds and circuit breaking.

### E3: Inference with premises

The code is not directly expressed and needs to be inferred based on context.
At this time, the premises and uncertainties must be written clearly and cannot be disguised as facts.

## 3. An actual judgment example

Suppose we want to write the conclusion:
"The real boundary of the permission system lies in the order of determination, not in the UI pop-up window."

You can put the evidence like this:

```text
E1: filesystem.ts 中 read/write 判定顺序是固定链条
E2: permissionSetup.ts 对危险规则做前置拦截
E3: 在团队默认配置下，这种顺序更适合共享工作区
```

The advantage of writing this way is that readers can accurately know which part is fact and which part is judgment.

## 4. Minimum process when writing

Each key conclusion goes through four steps:

1. Find the anchor file first.
2. Then write down the observed facts.
3. Then give the level of evidence.
4. Finally, give an explanation of the design.

You will find that this is exactly the opposite of "have an opinion first and then look for evidence."
This is where the difference in quality comes from.

## 5. Common misuse (also the easiest place to overturn)

### Misuse 1: Write E3 as E1

Typical sentence patterns:
"The author obviously wants to..."
If such a sentence has no annotation or branching evidence, it is an inference, not a fact.

### Misuse 2: Only module name, no positioning

Just writing "in the permission module" makes no sense.
At least give it a path-level anchor, such as `src/utils/permissions/filesystem.ts`.

### Misuse 3: Cross-file behavior does not close the loop

Only seeing the call point without looking at the called implementation makes us rush to conclusions.
This reduces E2 to a "guessing puzzle".

## 6. Why is this set of constraints worth the cost?

It’s true that evidence annotation increases editing costs.
But it brings three direct benefits:

- Team discussions can come back to the same set of facts.
- Newcomers don’t need to guess at authorial intent when they take over.
- Articles can go directly into the architecture review materials instead of being read as blogs only.

## 7. A suggested way to write a paragraph

You can use this fixed sentence pattern:

```markdown
结论：……
证据等级：E1/E2/E3
代码锚点：……
边界条件：……
```

After using it a few times, you will obviously feel that the quality of the article is more stable.

## 8. Next step

Read `runtime-entry-and-turn-lifecycle` first.
That article will directly demonstrate how to incorporate the evidence rules into a complete operational link in the mechanism text.
