# Current Sprint

## Sprint

Sprint 2A — Video Delivery and Approved YouTube Upload

## Objective

Turn an approved CreatorForge content project into a locally rendered YouTube
video and allow the creator to explicitly upload it to their own YouTube
channel as a private video.

## Status

In progress — Sprints 2A.1 and 2A.2 completed. Do not begin Sprint 2A.3
without explicit approval.

## Product Outcome

The first end-to-end automated YouTube workflow is:

```text
Approved project → local narration → reviewed MP4 → explicit approval → private YouTube upload
```

CreatorForge remains local-first and creator-directed. It must never publish
without an explicit user action.

## Delivery Increments

### 2A.1 — Voice (Completed)

- [x] Convert an approved script to local narration through the local Kokoro
  integration.
- [x] Save `voice.wav` and persist its path, provider, sample rate, and
  duration metadata with the project.
- [x] Make saved narration available through a creator-initiated Play Voice
  control.
- [x] Provide a clear unavailable-provider error when local TTS dependencies
  are missing.
- [ ] Allow a creator-supplied WAV or MP3 narration as a fallback. This is
  deferred to Sprint 2A.2 because it requires the project-media selection UI.

### 2A.2 — Video (Completed)

- [x] Render a 16:9 1920x1080, 30 FPS, H.264/AAC MP4 through local FFmpeg.
- [x] Support **User Images** only: creator-supplied JPG, PNG, or WebP files in
  `outputs/<project>/images/`.
- [x] Persist video metadata and provide creator-initiated HTML5 preview.
- [x] Generate an SRT subtitle artifact from planned script scenes when requested.
- [x] Support opt-in manual, AI, and mixed visual-mode rendering while
  preserving the original no-body user-image render behavior.
- [ ] Custom timeline editing, stock media, and generative video. Out of scope.

FFmpeg must be installed locally and available on `PATH` (or configured through
`CREATORFORGE_FFMPEG_BIN`) before rendering. Automated verification uses a
mocked FFmpeg process; no FFmpeg binary is installed in this workspace.

### 2A.3 — Upload

- Authenticate the creator with the official YouTube Data API OAuth flow using
  the least-privilege `youtube.upload` scope.
- Upload the approved MP4 with the selected project title, description, tags,
  thumbnail, category, and explicit privacy setting.
- Default uploads to private and show upload and processing status.
- Persist only the resulting YouTube video ID and non-secret upload metadata;
  keep OAuth credentials local, outside source control, with restricted access.

## Approved Integrations

- A maintained local TTS tool for narration, subject to license and platform
  validation during 2A.1.
- FFmpeg CLI for media assembly, encoding, subtitles, and image sequencing.
- Local ComfyUI for AI scene images through the dedicated client boundary.
- Official YouTube Data API and OAuth 2.0 for upload. Do not automate the
  YouTube browser UI.

## Architecture and Compatibility Constraints

- Preserve the frozen backend architecture and all existing API contracts.
- Keep routes thin; generation coordination remains in `generator.py`.
- Keep project filesystem and asset persistence in project services.
- Keep each external tool behind a narrow client boundary; do not build a media
  engine, speech engine, or upload protocol.
- Add new endpoints only as additive, version-compatible project capabilities.
- Keep source media, rendered files, and credentials out of Git.
- No autonomous, scheduled, public, or irreversible publishing.

## Acceptance Criteria

- [ ] A creator can select or provide narration for an existing project.
- [x] A creator can select User Images, AI Images, or Mixed visuals before rendering.
- [x] CreatorForge renders a playable 1080p MP4 and optionally writes an SRT file locally.
- [ ] The creator can review the rendered file before an upload control is
  available.
- [ ] An explicit upload action performs OAuth consent and uploads the file as
  private by default.
- [ ] The upload result includes a video ID/link and processing state.
- [ ] Existing generation, saving, project opening, and export behavior remains
  compatible.
- [ ] Tests mock all external integrations; any local-tool smoke test is
  optional and separate.

## Non-Goals

- Custom video timeline editing.
- Stock media library, marketplace, or asset search.
- Generative video, voice cloning, or automatic public publishing.
- Shorts, blog, social, analytics, team collaboration, or scheduled workflows.
- A general provider abstraction or backend refactor.

## Planning Gates

1. Before 2A.1: approve the specific TTS implementation after validating its
   maintenance, license, Windows support, and required model download.
2. Before 2A.2: approve the project-media persistence shape and the local
   image-provider boundary for AI Images.
3. Before 2A.3: approve OAuth credential storage, redirect/callback handling,
   and the YouTube API project configuration.

## Verification Strategy

- Unit-test media manifests, visual-mode validation, metadata mapping, and
  command construction.
- Mock TTS, FFmpeg, image integration, and YouTube API clients in service/API
  tests.
- Manually smoke-test each increment locally with creator-approved sample
  assets; do not contact Ollama for normal verification.
