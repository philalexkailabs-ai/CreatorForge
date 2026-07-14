# CreatorForge Installation Guide

Install Python 3.10+, then create and activate a virtual environment and run
`pip install -r requirements.txt`. Install Ollama and pull a supported model.

For the full local pipeline, install ComfyUI with the SDXL Turbo checkpoint,
Kokoro plus espeak-ng, and FFmpeg on `PATH`. Start the API with
`uvicorn backend.main:app --reload` and serve `frontend/` with a local static
server. Configure local paths and URLs from Settings before running the full
pipeline.

YouTube uploads require a desktop OAuth client file. Configure its local path
in Settings; credentials and tokens must remain outside source control.
