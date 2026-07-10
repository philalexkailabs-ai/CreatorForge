# Current Sprint

## Sprint

Sprint 0.6.4 — Research Distillation Engine

## Objective

Distill full research into a concise summary before downstream generation, reducing prompt size while preserving quality and retaining the full research artifact.

## Status

Completed

## Files Expected

- `backend/prompts.py`
- `backend/services/generator.py`
- `backend/main.py`
- `backend/services/project_saver.py`
- `backend/services/project_service.py`
- `frontend/index.html`
- `frontend/js/app.js`

## Acceptance Criteria

- [x] Research summary prompt exists.
- [x] Project generation runs research then research summary.
- [x] Downstream stages use the summary rather than full research.
- [x] Summary is saved, reopened, and shown in the UI.
- [x] Legacy projects return an empty summary.

## Engineering Checklist

- [x] No endpoint or request changes.
- [x] No response fields removed.
- [x] Existing architecture extended without new top-level services.
- [x] Mock-only verification completed.
