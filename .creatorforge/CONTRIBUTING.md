# Contributing to CreatorForge

## Repository Setup

1. Clone the repository.
2. Install documented Python dependencies.
3. Run local Ollama with an approved supported model.
4. Start the FastAPI backend and serve the frontend for local development.

## Required Reading Order

1. [AI Memory](AI_MEMORY.md)
2. [Architecture](ARCHITECTURE.md)
3. [Decisions](DECISIONS.md)
4. [Coding Standard](CODING_STANDARD.md)
5. [Current Sprint](CURRENT_SPRINT.md)
6. Relevant roadmap, backlog, prompt, testing, or security documents.

## Coding Standards

Follow [Coding Standard](CODING_STANDARD.md), [Prompt Rules](PROMPT_RULES.md), and the architecture freeze.

## Commit Messages

Use focused, descriptive commit messages that identify the feature or fix. Keep generated outputs and unrelated work out of commits.

## Review Process

Explain scope before editing, verify proportionally, confirm compatibility, and document remaining debt. The developer gives final approval.

## Pull Requests

Keep pull requests focused on one sprint or coherent feature. Include purpose, changed files, testing, compatibility notes, and documentation updates.

## Architecture Approval

Do not refactor or add architectural layers without approval. A proposal is allowed only when a bug requires it, a feature cannot fit the existing architecture, or the developer explicitly requests architectural change.
