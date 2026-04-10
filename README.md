# Lessons from Claude Code

An engineer-focused handbook for deconstructing and rebuilding the Coding Agent architecture extracted from Claude code. This repository is bilingual and generated from Markdown sources.

- Read online: https://lessons-from-claude-code.netlify.app/
- Content source: `contents/` Markdown files automatically generated into `html-site/`
- Default entry: English, with Chinese/English toggle support

## Project Purpose

This project focuses on extracting reusable engineering patterns:

- Query loop and conversation lifecycle
- Tool system (contracts, dispatch, execution)
- Permissions and security boundaries
- Context budget and compression strategy
- Multi-agent collaboration and practical engineering delivery

## Content Navigation

- `Map`: reading path, terminology, evidence conventions
- `Mechanism`: how the system operates
- `Decision`: why the design is this way
- `Build`: how to implement minimally and ship reliably

## Quick Start

### 1) View the static site locally

Open: `html-site/index.html`

### 2) Rebuild the site from Markdown

```bash
python scripts/build_site.py
```

Built output is in: `html-site/`

## Repository Structure

```text
contents/              # article source files (zh + en)
scripts/build_site.py  # site generation script
html-site/             # static site output (ready to deploy)
claude-code-main/      # code snapshot for reference anchors
```

## Writing and Editing Conventions

- Each article includes explicit code anchors (`path + symbols`)
- Distinguish facts, cross-file evidence, and inference
- Prioritize explaining mechanisms and tradeoffs over implementation details
- Keep Chinese and English content structurally aligned

## Who This Is For

- Engineers building Coding Agents / AI IDEs / Agent runtimes
- Teams implementing permission governance, tool orchestration, and context management
- Developers who want to move from "demo working" to "sustainably running system"

## Contribution

Contributions are welcome via Issues / PRs for:

- corrections and evidence supplements
- new article proposals (mechanism / decision / reconstruction)
- build scripts and site experience improvements
