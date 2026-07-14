"""Best-effort local startup diagnostics; never contacts generation providers."""
from __future__ import annotations

import importlib.util
import os
import shutil
from pathlib import Path

from backend.services.settings_service import get_settings


def get_diagnostics() -> dict[str, object]:
    settings = get_settings()
    ffmpeg = str(settings["ffmpeg_path"])
    client_secret = str(settings["youtube_client_secrets"])
    return {
        "ollama": _url_status(str(settings["ollama_url"])),
        "comfyui": _url_status(str(settings["comfyui_url"])),
        "ffmpeg": _status(bool(shutil.which(ffmpeg) or Path(ffmpeg).is_file()), "FFmpeg executable"),
        "kokoro": _status(importlib.util.find_spec("kokoro") is not None, "Kokoro package"),
        "cuda": _status(_cuda_available(), "CUDA availability"),
        "youtube_credentials": _status(bool(client_secret and Path(client_secret).is_file()), "OAuth client secrets"),
    }


def _url_status(value: str) -> dict[str, str]:
    return _status(value.startswith(("http://", "https://")), "Configured local URL")


def _status(available: bool, label: str) -> dict[str, str]:
    return {"status": "green" if available else "yellow", "detail": label if available else f"{label} needs configuration"}


def _cuda_available() -> bool:
    return bool(os.getenv("CUDA_VISIBLE_DEVICES"))
