# AI Context

## Current Architecture

CreatorForge uses a static HTML/CSS/JavaScript frontend, FastAPI routes, a central generator service, an Ollama client, project services, and filesystem outputs. See [Architecture](ARCHITECTURE.md).

## Current Sprint

Sprint 0.6.4, Research Distillation Engine, is completed. See [Current Sprint](CURRENT_SPRINT.md).

## Completed Features

- Local Ollama generation with configured model selection.
- Research, research summary, outline, titles, script, description, tags, and thumbnail artifacts.
- Context-aware downstream generation.
- Project saving, history, reopening, and legacy fallback behavior.
- In-memory live generation progress.
- Prompt quality and lightweight output cleanup.

## Future Roadmap

Use [Roadmap](ROADMAP.md) for planned releases and [Backlog](BACKLOG.md) for unprioritized work.

## Things Never to Change Without Approval

- The frozen backend architecture.
- Existing endpoint URLs, request schemas, and response contracts.
- Local-first Ollama support.
- Separation between routes, generator behavior, provider access, and project filesystem behavior.

## Coding Philosophy

Deliver focused end-user value. Extend existing modules. Preserve compatibility. Avoid speculative refactors and unnecessary complexity.

## How Codex Should Behave

- Read this folder before coding.
- Analyze scope before editing.
- Explain files to be changed before editing when required.
- Do not propose architectural changes unless a bug requires it, a feature cannot fit the current architecture, or the user explicitly requests one.
- Verify work without invoking external generation when practical.

## How AI Should Review Code

- Check user-facing behavior first.
- Check contracts and compatibility.
- Verify architecture boundaries remain intact.
- Identify concrete defects and debt; do not turn a review into unapproved refactoring.
