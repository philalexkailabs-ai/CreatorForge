# Product Principles

## Local First

**Description:** CreatorForge is designed to work with local AI models through Ollama.

**Reason:** Creators should retain control of their data, cost, and workflow.

**CreatorForge example:** The Ollama client sends generation prompts to a locally running model.

## Creator First

**Description:** Features should improve a creator's ability to plan, create, review, and reuse content.

**Reason:** Engineering choices are valuable only when they improve the creator journey.

**CreatorForge example:** Research, outlines, titles, scripts, and thumbnail prompts are saved as editable project artifacts.

## AI Assists Humans

**Description:** AI creates drafts and options; the creator remains the final decision-maker.

**Reason:** Human judgment protects brand voice, accuracy, and intent.

**CreatorForge example:** Generated artifacts are displayed for review rather than automatically published.

## Transparency

**Description:** The system should make its work and limitations understandable.

**Reason:** Creators need confidence in what was generated and why.

**CreatorForge example:** Live progress identifies the current generation stage, while projects retain research and summaries.

## Simplicity

**Description:** Prefer direct, understandable implementation over unnecessary abstraction.

**Reason:** CreatorForge must remain maintainable by a small team.

**CreatorForge example:** Project history uses the existing filesystem and project metadata rather than an early database.

## Architecture Stability

**Description:** Preserve the frozen backend architecture unless a bug, a non-fitting feature, or explicit approval requires change.

**Reason:** Stable boundaries reduce regression risk and AI-agent drift.

**CreatorForge example:** New generation stages extend `generator.py` instead of creating endpoint-specific services.

## Reuse Before Rewrite

**Description:** Extend working modules and shared helpers before replacing them.

**Reason:** Reuse preserves contracts and avoids duplicated logic.

**CreatorForge example:** New prompt context fields use the existing generator context builder.

## Performance Matters

**Description:** Use model context and browser/network work thoughtfully.

**Reason:** Local generation can be slow and resource constrained.

**CreatorForge example:** Research is distilled before it is passed to downstream generation stages.

## Privacy by Default

**Description:** Treat creator topics, research, and generated assets as private local data by default.

**Reason:** Content plans may contain sensitive business or personal information.

**CreatorForge example:** Project files are saved locally under `outputs/` and generation uses local Ollama.

## Explainability

**Description:** Preserve enough source artifacts for a creator to understand a generated result.

**Reason:** Review is stronger when drafts have visible context.

**CreatorForge example:** A project includes research, research summary, outline, and downstream content artifacts.

## Human Approval Before Automation

**Description:** Do not automatically publish, delete, or make irreversible external changes without explicit approval.

**Reason:** Automation must remain accountable to the creator.

**CreatorForge example:** Current workflows generate and save content but do not publish it.

## Consistency Over Cleverness

**Description:** Use repeatable patterns, names, and contracts across features.

**Reason:** Consistency makes the system easier to review, maintain, and extend.

**CreatorForge example:** All core artifacts are consistently generated, persisted, opened, and rendered.
