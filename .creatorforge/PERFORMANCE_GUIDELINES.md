# Performance Guidelines

## Prompt Optimization

Write concise prompts with clear output requirements. Avoid redundant instructions and unnecessary context.

## Context Reduction

Use distilled artifacts when available. CreatorForge currently passes research summaries downstream while retaining complete research as a project artifact.

## Caching

Use lightweight, session-only caches when they improve visible responsiveness and do not create stale persistent state.

## Streaming

Consider streaming only when it provides clear creator value and the API/progress contract can support it.

## Parallel Generation

Parallelism can reduce latency but may overload local models or break artifact dependencies. Measure and approve it before use.

## Token Reduction

Track prompt growth as new context is added. Prefer summaries, bounded sections, and artifact-specific context.

## Memory Usage

Avoid loading unnecessary projects or holding large generated content in memory longer than needed.

## Frontend Responsiveness

Keep the interface responsive during generation, provide clear stage feedback, and avoid blocking the main browser thread.

## Backend Responsiveness

Keep routes focused, use timeouts when approved, and measure stage duration before introducing complex infrastructure.
