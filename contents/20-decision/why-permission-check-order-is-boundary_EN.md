---
title: Why is the order of permission determination itself a security boundary?
slug: why-permission-check-order-is-boundary
summary: Explain why the evaluation order of deny/ask/allow is more critical than the pop-up copy, and how to prevent implicit
  privilege escalation.
track: decision
category: decision
order: 21
tags:
- decision
- permissions
- security-boundary
level: advanced
depth: L3
evidence_level: E2
code_anchors:
- path: claude-code-main/src/utils/permissions/filesystem.ts
  symbols:
  - read order
  - write order
- path: claude-code-main/src/utils/permissions/permissionSetup.ts
  symbols:
  - unsafe rule lint
prerequisites:
- permissions-runtime-evaluation
status: published
updatedAt: '2026-04-06'
lang: en
translation_of: why-permission-check-order-is-boundary
---

# Why is the order of permission determination itself a security boundary?

> This article is not "how to write the permission mechanism", but "why the judgment order is the boundary ontology".
> If the order is wrong, no matter how many configurations are configured, it may be misaligned protection.

## 1. Start with a real decision conflict

Products often ask for:
"Enable this command by default and stop popping up windows all the time."

Security will make counter-requirements:
"This command must pass the deny rule first and cannot first look at the allow rule."

This is actually not a simple conflict between experience vs. safety, but a conflict over "whether the order can be destroyed."

## 2. Why order is more critical than the number of rules

Let's say you have 20 rules, but the order isn't stable.
Then the system will hit different priorities on different paths, and the behavior will be unpredictable.

The core idea displayed by `claude-code-main/src/utils/permissions/filesystem.ts` is:
Define the sequential contract first, then allow the rules to be extended.

A reliable chain is usually:

```text
hard deny -> ask -> explicit allow -> implicit default
```

## 3. Sequence is “provability”

If the team asks, “Why was it released this time?”
You need to be able to answer:

1. Which rule was hit.
2. Why the previous stronger rule didn't hit.
3. The final decision is subject to additional security checks.

These three things can only be proven if the order is stable.

## 4. Why “the user clicks to agree” cannot be the final outcome

Many implementations treat user confirmation as final.
But in a production system, user confirmation should be a step in the chain, not a backdoor to skip the chain.

In particular, write operations and shell execution should still be subject to structural security checks.
Otherwise, there will be a combined risk of "user accidental touch + full system release".

## 5. The defense line during the configuration loading phase cannot be omitted.

`claude-code-main/src/utils/permissions/permissionSetup.ts` reflects another key decision:
Dangerous rules need to be discovered at load time, rather than left to chance at run time.

The value of this type of pre-lint is to advance the risk from execution risk to configuration risk.

## 6. Common anti-patterns

### Anti-pattern A: According to the order of definition of functional modules

One file system, one shell, and one MCP.
In the end, neither users nor developers can establish unified expectations.

### Anti-Pattern B: Inserting "Special Case Shortcuts"

In order to quickly go online for a certain scene, insert an "allow first and then talk" in the chain.
It saves trouble in the short term, but is an audit disaster in the long term.

### Anti-pattern C: The log only records the conclusion but not the path

Only remembering `allowed=true` but not the hit rule chain makes review almost impossible.

## 7. Engineering advice: treat order as API

Once the priority order is determined, treat it as a public contract:

- Write tests to ensure that the order does not regress.
- Write documents describing the responsibilities of each layer.
- Write log output hit path.

This improves real security more than "adding another layer of pop-ups".

## 8. Summary

The "boundary" of the permission system is not a rule or a button.
Boundaries are the order in which rules run and their non-bypassability.

## Next Read
- `build-a-safe-tool-runtime`
