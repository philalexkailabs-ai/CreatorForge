# Testing Strategy

## Philosophy

Tests should protect creator-facing behavior, contracts, and frozen architecture boundaries. They should be proportionate to risk and runnable without a real Ollama model whenever possible.

## Unit Tests

Test focused functions such as prompt context construction, output cleanup, model validation, metadata fallback, and artifact parsing.

## Integration Tests

Test collaboration between generator, Ollama-client mocks, project saving, project loading, and progress lifecycle.

## API Tests

Test request validation, response contracts, known error responses, project history/opening, model selection, and generation status.

## Frontend Tests

Test request payloads, rendering of project artifacts, progress polling, cache behavior, and safe text insertion.

## Mocking Ollama

Mock the Ollama client for normal test runs. Keep any real local-model smoke test separate, optional, and clearly labeled.

## Regression Tests

Every fixed defect should receive a focused regression test when practical. Preserve existing endpoint and artifact behavior as features are added.

## Manual Testing

Manually verify local startup, selected-model generation, saved project reopening, and visible error states before a release candidate.

## Definition of Done

- Relevant unit and integration checks pass.
- API contracts remain compatible.
- No unrelated files change.
- Documentation and changelog are updated when required.
- A human approves user-facing behavior.

## Future CI/CD

Add formatting, linting, type checks, automated tests, and release checks to CI before production deployment. See [Deployment Strategy](DEPLOYMENT_STRATEGY.md).
