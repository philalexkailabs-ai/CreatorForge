# Architectural Decisions

## Architecture Freeze

- **Date:** 2026-07-11
- **Status:** Active
- **Decision:** Keep the backend architecture stable and extend existing modules by default.
- **Reason:** The project is small and understandable. Refactoring is permitted only for a bug, a feature that cannot fit the existing design, or explicit user approval.

## Generator Service

- **Date:** 2026-07-10
- **Status:** Active
- **Decision:** Keep content generation in `backend/services/generator.py`.
- **Reason:** It groups generation by domain instead of creating a service for every endpoint or artifact.

## Research Summary

- **Date:** 2026-07-11
- **Status:** Active
- **Decision:** Persist full research but pass its distilled summary to downstream stages.
- **Reason:** This reduces prompt size while retaining a detailed research artifact for creators.

## Project History

- **Date:** 2026-07-10
- **Status:** Active
- **Decision:** Keep project filesystem behavior in project services and use application-owned metadata.
- **Reason:** Metadata survives copying and backup better than filesystem timestamps alone.

## Progress Engine

- **Date:** 2026-07-11
- **Status:** Active
- **Decision:** Use one lightweight in-memory status object and polling.
- **Reason:** It provides useful local progress without queues, persistence, or websockets.

## Context Builder

- **Date:** 2026-07-11
- **Status:** Active
- **Decision:** Build prompt context centrally inside `generator.py`.
- **Reason:** It prevents duplicated prompt assembly and allows new context fields to be introduced consistently.
