# Technical Debt

## High Priority

### Timeout Handling

- **Problem:** Ollama requests do not yet define robust timeouts.
- **Impact:** A stalled model can leave the creator waiting indefinitely.
- **Recommended solution:** Add configured request timeouts and clear API error mapping.
- **Estimated difficulty:** Medium.

### Prompt Validation

- **Problem:** Prompts improve output format but do not guarantee model compliance.
- **Impact:** Invalid counts, lists, or artifact formats can reach creators.
- **Recommended solution:** Add artifact-specific validation and approved retry behavior.
- **Estimated difficulty:** Medium.

### Testing

- **Problem:** Verification is currently ad hoc rather than a committed automated suite.
- **Impact:** Regression risk grows with each sprint.
- **Recommended solution:** Add unit, service, API, and frontend test coverage following [Testing Strategy](TESTING_STRATEGY.md).
- **Estimated difficulty:** High.

### Project Identity

- **Problem:** Topic-derived folders can overwrite projects with the same topic.
- **Impact:** Creator work may be replaced unintentionally.
- **Recommended solution:** Use stable project-ID directories in an approved future migration.
- **Estimated difficulty:** Medium.

## Medium Priority

### Retry Engine

- **Problem:** Transient model or local service failures are not retried.
- **Impact:** Creators may need to restart complete generation.
- **Recommended solution:** Add bounded, artifact-aware retries after validation rules are approved.
- **Estimated difficulty:** Medium.

### Token Counting

- **Problem:** Prompt size is not measured before local generation.
- **Impact:** Large research or scripts may exceed useful model context.
- **Recommended solution:** Track context size and apply approved summarization limits.
- **Estimated difficulty:** Medium.

### Performance Metrics

- **Problem:** Stage duration and local model performance are not recorded.
- **Impact:** Bottlenecks are difficult to identify.
- **Recommended solution:** Add privacy-conscious local timing metrics.
- **Estimated difficulty:** Medium.

### Streaming Generation

- **Problem:** Artifact results are delivered only after each full request completes.
- **Impact:** Long scripts feel less responsive.
- **Recommended solution:** Evaluate streaming after progress and error contracts are designed.
- **Estimated difficulty:** High.

### Project Search, Delete, and Rename

- **Problem:** History supports listing and opening only.
- **Impact:** Projects become harder to manage as the library grows.
- **Recommended solution:** Add approved project-service operations and focused UI actions.
- **Estimated difficulty:** Medium.

### Analytics

- **Problem:** Creator performance feedback is not part of the product.
- **Impact:** The system cannot learn from content outcomes.
- **Recommended solution:** Design opt-in analytics and project metrics.
- **Estimated difficulty:** High.

### Background Jobs

- **Problem:** Generation runs within the request lifecycle.
- **Impact:** Long jobs are limited by the current process model.
- **Recommended solution:** Evaluate job orchestration only when feature scale requires it.
- **Estimated difficulty:** High.

## Low Priority

### Database Migration

- **Problem:** Project metadata is filesystem-based.
- **Impact:** Advanced search and multi-user workflows are limited.
- **Recommended solution:** Introduce a database only after local project workflows require it.
- **Estimated difficulty:** High.

### Deployment

- **Problem:** Production deployment is not implemented.
- **Impact:** CreatorForge remains development/local focused.
- **Recommended solution:** Follow [Deployment Strategy](DEPLOYMENT_STRATEGY.md) in a dedicated release sprint.
- **Estimated difficulty:** High.

### Docker

- **Problem:** There is no maintained container workflow.
- **Impact:** Environment setup may vary across machines.
- **Recommended solution:** Add Docker after runtime configuration is formalized.
- **Estimated difficulty:** Medium.

### Authentication

- **Problem:** No user identity layer exists.
- **Impact:** Hosted or team use is not supported safely.
- **Recommended solution:** Design authentication only for an approved multi-user deployment scope.
- **Estimated difficulty:** High.
