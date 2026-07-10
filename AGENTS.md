# CreatorForge AI Engineering Guide

## Required Session Start

Before making changes, read the governance documents in `.creatorforge/`, especially:

- `.creatorforge/AI_CONTEXT.md`
- `.creatorforge/ARCHITECTURE.md`
- `.creatorforge/CODING_STANDARD.md`
- `.creatorforge/DECISIONS.md`
- `.creatorforge/CURRENT_SPRINT.md`

Use `.creatorforge/ROADMAP.md`, `.creatorforge/BACKLOG.md`, and `.creatorforge/PROMPT_RULES.md` when relevant.

## Core Rules

- Analyze before modifying.
- Keep changes focused and explain files that will change before editing.
- Preserve backward compatibility unless explicitly approved otherwise.
- Keep routes thin, generation in the generator service, provider access in the Ollama client, and filesystem behavior in project services.
- The backend architecture is frozen. Do not propose refactoring unless a bug requires it, a feature cannot fit the current architecture, or the user explicitly requests it.
- Prefer end-user value over speculative engineering work.

## Review and Delivery

- Verify changes proportionally without contacting Ollama when practical.
- Do not modify unrelated files.
- Report changed files, compatibility, verification, and remaining debt for completed implementation tasks.
