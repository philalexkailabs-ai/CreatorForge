# CreatorForge Changelog

## Sprint 2A.1 — Voice Engine

Added local Kokoro narration generation, `voice.wav` persistence and metadata,
voice playback for generated and reopened projects, and mock-based regression
coverage without Ollama.

## Sprint 0.6.4 — Research Distillation Engine

Added a research-summary artifact, summary persistence and loading, summary UI card, and summary-led downstream context.

## Sprint 0.6.3 — Live Generation Progress

Added in-memory generation stage status, a status API route, and frontend polling with stage-level progress display.

## Sprint 0.6.2 — Prompt Quality Engine

Strengthened output-only prompt rules and added shared lightweight cleanup for fences, quotes, whitespace, and repeated blank lines.

## Sprint 0.6.1 — Context-Aware Generation

Added centralized prompt context construction and passed upstream artifacts into downstream project generation.

## Sprint 0.6.0 — AI Research Pipeline

Added research, outline, and thumbnail prompt as first-class project artifacts with persistence and reopening support.

## Sprint 0.5.4 — Project Opening

Added project detail loading by ID, legacy fallbacks, sidebar project opening, and session-only project caching.

## Sprint 0.5.3 — Project History

Added application-owned project metadata, project listing, saved-project sidebar loading, and graceful legacy handling.

## Sprint 0.5.2 — Model Selection

Connected the frontend selector to backend model validation and configured supported/default Ollama models.

## Sprint 0.5.1 — Thumbnail Prompt Generation

Added standalone thumbnail prompt generation and the initial thumbnail artifact UI.

## Sprint 0.5.0 — Studio Foundation

Established the combined project-generation workflow, prompt templates, local Ollama integration, and initial Studio UI.
