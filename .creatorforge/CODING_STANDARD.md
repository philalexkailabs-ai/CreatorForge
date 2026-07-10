# CreatorForge Coding Standard

## Naming Conventions

- Use descriptive snake_case for Python modules, functions, and variables.
- Use clear camelCase for JavaScript functions and variables.
- Name artifacts consistently across prompts, API payloads, persistence, and UI.

## Folder Rules

- Keep generation code in `backend/services/generator.py`.
- Keep project filesystem work in project services.
- Keep provider communication in `backend/ollama.py`.
- Keep application data in `outputs/`.
- Do not create folders or services without an approved need.

## Python Style

- Use type hints where practical.
- Keep functions small and focused.
- Prefer constants and named values over repeated literals.
- Use explicit error behavior for expected failures.

## JavaScript Style

- Use `const` by default and `let` only when reassignment is needed.
- Use `textContent` for generated text.
- Keep API calls and DOM updates straightforward.
- Do not add frameworks without approval.

## Service Rules

- One service owns one coherent domain.
- Avoid endpoint-specific services.
- Do not duplicate filesystem or generation logic.

## Route Rules

- Keep routes thin.
- Validate request input, call the existing service layer, and return a response.
- Do not put filesystem or prompt-building logic in routes.

## Prompt Rules

- Prompts describe the task and output rules.
- Context assembly belongs in the generator context builder.
- Prefer output-only instructions and stable formats.

## Documentation Rules

- Update governance files when a completed sprint materially changes product behavior or an architectural decision.
- Keep documentation factual, concise, and linked to related governance files.

## Git Commit Rules

- Use focused commits with clear messages.
- Do not include generated output or unrelated changes.
- Test proportionally before committing.

## Review Checklist

- [ ] Scope is limited to the requested feature.
- [ ] Existing contracts remain compatible.
- [ ] Relevant syntax and behavior checks pass.
- [ ] No unrelated files changed.
- [ ] Documentation is updated when required.
