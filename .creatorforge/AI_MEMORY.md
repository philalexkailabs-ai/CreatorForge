# CreatorForge AI Memory

## Purpose

This is the primary persistent memory file for future AI coding agents. Read it first, then read the linked governance documents before making changes.

## Current Architecture

CreatorForge is a local-first AI content studio with a static HTML/CSS/JavaScript frontend, FastAPI routes, a central generator service, an Ollama client, project services, and filesystem outputs. See [Architecture](ARCHITECTURE.md).

## Completed Features

- Local Ollama generation and configured model selection.
- Research, research summary, outline, titles, script, description, tags, and thumbnail prompt artifacts.
- Context-aware generation using research summaries downstream.
- Output-only prompt rules and lightweight cleanup.
- Project metadata, saving, history, opening, and legacy fallback.
- Session-only project caching and live generation progress.
- Local Kokoro narration saved as `voice.wav`, with persisted metadata and
  creator-initiated playback.

## Things Never to Change Without Approval

- Frozen backend architecture.
- Existing endpoint URLs, request schemas, and response contracts.
- Local-first Ollama support.
- Route, generator, provider, and project-service responsibility boundaries.

## Product Philosophy

Local first, creator first, transparent AI assistance, privacy by default, human approval before automation, simplicity, and consistency over cleverness. See [Product Principles](PRODUCT_PRINCIPLES.md).

## Roadmap

The product is in v0.6 Alpha. Use [Roadmap](ROADMAP.md), [Backlog](BACKLOG.md), and [Versioning](VERSIONING.md) for future planning.

## Current Sprint

Sprint G-002 is completed: the engineering knowledge base now provides persistent governance and workflow memory.

## Future Direction

Prioritize creator-facing workflow improvements: editing, exports, project management, brand context, multi-platform content, publishing, analytics, and automation—only through approved, focused sprints.

## Agent Behavior

- Read this file, [Decisions](DECISIONS.md), [Architecture](ARCHITECTURE.md), [Coding Standard](CODING_STANDARD.md), and [Current Sprint](CURRENT_SPRINT.md) before coding.
- Extend existing modules and preserve contracts.
- Propose architecture changes only under the approved architecture-freeze rules.
- Verify safely and report scope, compatibility, verification, and remaining debt.
